"""
WhatsApp views for:
- Feature #38: Manual Reminder Trigger
- Feature #43: Interaction listing
- Webhook handling (Day 4 — handled by Member A, added here for completeness)
"""
from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import WhatsAppInteraction
from .serializers import WhatsAppInteractionSerializer
from apps.doses.models import DoseLog
from services.whatsapp_service import send_whatsapp_message
import os


def get_whatsapp_error_message() -> str:
    """Helper to return dynamic, helpful error message based on credentials."""
    if os.environ.get('WHATSAPP_ACCESS_TOKEN') and os.environ.get('WHATSAPP_PHONE_NUMBER_ID'):
        return (
            "Official Meta WhatsApp API send failed. Check backend console logs. "
            "If using a Sandbox account, make sure the recipient phone number is added "
            "to the 'Allowed / Verified Sandbox Numbers' list in your Meta Developer Console."
        )
    elif os.environ.get('CALLMEBOT_APIKEY'):
        return "CallMeBot WhatsApp send failed. Please check your apiKey or phone number configuration."
    else:
        return "No WhatsApp API credentials configured (WHATSAPP_ACCESS_TOKEN or CALLMEBOT_APIKEY). Simulated send logged."


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_reminder_manual(request):
    """
    Feature #38: Manual Reminder Trigger
    POST /api/whatsapp/send-reminder/ — manually trigger a WhatsApp reminder for any dose.
    """
    patient_id = request.data.get('patient_id')
    dose_log_id = request.data.get('dose_log_id')
    
    dose_log = None
    if patient_id:
        from apps.patients.models import PatientProfile
        try:
            if request.user.role == 'admin':
                patient = PatientProfile.objects.get(id=patient_id)
            else:
                patient = request.user.caretaker_profile.patients.get(id=patient_id)
        except Exception:
            return Response({'error': 'Patient not found or access denied'}, status=404)
            
        dose_log = DoseLog.objects.filter(patient=patient).first()
        if not dose_log:
            from apps.medicines.models import Medicine, MedicineSchedule
            medicine, _ = Medicine.objects.get_or_create(
                name="Test Aspirin",
                defaults={'dosage': '100mg', 'instructions': 'Take 1 tablet in the morning'}
            )
            schedule, _ = MedicineSchedule.objects.get_or_create(
                patient=patient,
                medicine=medicine,
                defaults={
                    'scheduled_time': timezone.now().time(),
                    'start_date': timezone.now().date(),
                    'is_active': True
                }
            )
            dose_log, _ = DoseLog.objects.get_or_create(
                schedule=schedule,
                scheduled_date=timezone.now().date(),
                scheduled_time=schedule.scheduled_time,
                defaults={
                    'patient': patient,
                    'medicine': medicine,
                    'status': 'pending'
                }
            )
    elif dose_log_id:
        try:
            dose_log = DoseLog.objects.get(id=dose_log_id, patient__user=request.user)
        except DoseLog.DoesNotExist:
            return Response({'error': 'Dose not found'}, status=404)
    else:
        return Response({'error': 'patient_id or dose_log_id required'}, status=400)

    from services.ai_message_service import generate_ai_variables
    from services.whatsapp_service import send_reminder
    variables = generate_ai_variables(dose_log.patient, dose_log)
    success = send_reminder(dose_log, dose_log.patient, variables)
    dose_log.reminder_sent = True
    dose_log.save()
    
    return Response({
        'success': success,
        'message': 'WhatsApp reminder triggered successfully!' if success else get_whatsapp_error_message(),
        'message_id': dose_log.id
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_interactions(request):
    """
    Feature #43: List WhatsApp interactions for authenticated user.
    GET /api/whatsapp/interactions/
    """
    interactions = WhatsAppInteraction.objects.filter(
        patient__user=request.user
    ).order_by('-sent_at')
    date_filter = request.GET.get('date')
    if date_filter:
        interactions = interactions.filter(sent_at__date=date_filter)
    return Response({
        'interactions': WhatsAppInteractionSerializer(interactions, many=True).data,
        'count': interactions.count(),
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # Webhook — no JWT required
def whatsapp_webhook(request):
    """
    Webhook handler for patient replies (1, 2, or 3).
    Handles: taken, reschedule +15min, not taking (triggers escalation).
    Implements stale message rejection (> 2 hours).
    """
    sender_phone = request.data.get('From', '').replace('+', '').strip()
    body = request.data.get('Body', '').strip()

    # Find latest pending (non-expired) interaction for this phone
    two_hours_ago = timezone.now() - timedelta(hours=2)
    interaction = WhatsAppInteraction.objects.filter(
        whatsapp_number__endswith=sender_phone[-10:],  # match last 10 digits
        status='sent',
        sent_at__gte=two_hours_ago,
    ).order_by('-sent_at').first()

    if not interaction:
        return Response({'error': 'No active interaction found or message expired'}, status=404)

    dose_log = interaction.dose_log

    if body == '1':  # Taken
        dose_log.status = 'taken'
        dose_log.taken_at = timezone.now()
        dose_log.save()
        reply = "✅ Great! Dose marked as taken. Keep it up!"

    elif body == '2':  # Reschedule +15 min
        new_time = timezone.now() + timedelta(minutes=15)
        dose_log.status = 'rescheduled'
        dose_log.save()
        interaction.rescheduled_to = new_time

        # Create a new DoseLog for the rescheduled time
        DoseLog.objects.create(
            schedule=dose_log.schedule,
            patient=dose_log.patient,
            medicine=dose_log.medicine,
            scheduled_date=dose_log.scheduled_date,
            scheduled_time=new_time.time(),
            status='pending',
        )
        reply = f"⏰ Got it! We'll remind you again at {new_time.strftime('%I:%M %p')}."

    elif body == '3':  # Not Taking — trigger escalation
        dose_log.status = 'missed'
        dose_log.missed_at = timezone.now()
        dose_log.save()
        # Trigger escalation to caretaker
        from services.escalation_service import trigger_caretaker_alert
        trigger_caretaker_alert(dose_log)
        reply = "❌ Noted. Your caretaker has been notified. Please take care!"

    else:
        reply = "❓ Please reply with 1 (Taken), 2 (Remind in 15 min), or 3 (Not taking)."
        return Response({'processed': False, 'reply': reply})

    interaction.response_received = body
    interaction.response_time = timezone.now()
    interaction.status = 'responded'
    interaction.save()

    # Send confirmation reply via WhatsApp
    send_whatsapp_message(interaction.whatsapp_number, reply)
    return Response({'processed': True, 'reply': reply})
