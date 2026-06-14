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


def _get_or_create_test_dose_log(request, dose_log_id, patient_id):
    from django.db.models import Q
    from apps.patients.models import PatientProfile
    from apps.medicines.models import Medicine, MedicineSchedule

    if dose_log_id:
        if request.user.role == 'admin':
            return DoseLog.objects.get(id=dose_log_id)
        else:
            return DoseLog.objects.get(
                id=dose_log_id,
                patient__caretakers__user=request.user
            )
    elif patient_id:
        if request.user.role in ('admin', 'caretaker'):
            patient = PatientProfile.objects.filter(Q(id=patient_id) | Q(user_id=patient_id)).first()
            if not patient:
                raise PatientProfile.DoesNotExist("Patient profile not found.")
        else:
            patient = PatientProfile.objects.filter(Q(id=patient_id) | Q(user_id=patient_id), user=request.user).first()
            if not patient:
                raise PatientProfile.DoesNotExist("Patient profile not found.")

        dose_log = DoseLog.objects.filter(patient=patient).order_by('-scheduled_date', '-scheduled_time').first()
        if not dose_log:
            medicine, _ = Medicine.objects.get_or_create(
                name="Demo Pill",
                defaults={"dosage": "1 tablet", "instructions": "Take after meals"}
            )
            schedule, _ = MedicineSchedule.objects.get_or_create(
                patient=patient,
                medicine=medicine,
                defaults={"scheduled_time": timezone.now().time(), "is_active": True}
            )
            dose_log = DoseLog.objects.create(
                schedule=schedule,
                patient=patient,
                medicine=medicine,
                scheduled_date=timezone.now().date(),
                scheduled_time=schedule.scheduled_time,
                status='pending'
            )
        return dose_log

    raise ValueError("Either dose_log_id or patient_id must be provided")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_reminder_manual(request):
    """
    Feature #38: Manual Reminder Trigger
    POST /api/whatsapp/send-reminder/ — manually trigger a WhatsApp reminder.
    Body: { "dose_log_id": X } or { "patient_id": Y }
    """
    patient_id = request.data.get('patient_id')
    dose_log_id = request.data.get('dose_log_id')
    try:
        dose_log = _get_or_create_test_dose_log(request, dose_log_id, patient_id)
    except (DoseLog.DoesNotExist, PatientProfile.DoesNotExist, ValueError) as e:
        return Response({'error': str(e)}, status=400)

    from services.ai_message_service import generate_ai_variables
    from services.whatsapp_service import send_reminder
    variables = generate_ai_variables(dose_log.patient, dose_log)
    success = send_reminder(dose_log, dose_log.patient, variables)
    dose_log.reminder_sent = True
    dose_log.save()
    recipient_phone = dose_log.patient.user.whatsapp_number or 'no phone'
    return Response({
        'success': success,
        'message': 'WhatsApp reminder sent successfully' if success else 'WhatsApp send failed',
        'recipient': recipient_phone,
        'dose_log_id': dose_log.id
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_escalation_manual(request):
    """
    Manually trigger a WhatsApp caretaker alert for a dose log.
    POST /api/whatsapp/trigger-escalation/
    Body: { "dose_log_id": X } or { "patient_id": Y }
    """
    if request.user.role not in ('admin', 'caretaker'):
        return Response({'error': 'Only admins or caretakers can trigger escalations'}, status=403)
        
    dose_log_id = request.data.get('dose_log_id')
    patient_id = request.data.get('patient_id')
    try:
        dose_log = _get_or_create_test_dose_log(request, dose_log_id, patient_id)
    except (DoseLog.DoesNotExist, PatientProfile.DoesNotExist, ValueError) as e:
        return Response({'error': str(e)}, status=400)

    from services.escalation_service import trigger_caretaker_alert
    try:
        trigger_caretaker_alert(dose_log)
        return Response({'success': True, 'message': 'WhatsApp caretaker alert triggered', 'dose_log_id': dose_log.id})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_voice_manual(request):
    """
    Manually trigger a Twilio bot voice call for a dose log.
    POST /api/whatsapp/trigger-voice/
    Body: { "dose_log_id": X } or { "patient_id": Y }
    """
    if request.user.role not in ('admin', 'caretaker'):
        return Response({'error': 'Only admins or caretakers can trigger voice calls'}, status=403)

    dose_log_id = request.data.get('dose_log_id')
    patient_id = request.data.get('patient_id')
    try:
        dose_log = _get_or_create_test_dose_log(request, dose_log_id, patient_id)
    except (DoseLog.DoesNotExist, PatientProfile.DoesNotExist, ValueError) as e:
        return Response({'error': str(e)}, status=400)

    from services.call_service import make_bot_call
    try:
        success = make_bot_call(dose_log)
        return Response({
            'success': success,
            'message': 'Twilio voice call triggered successfully' if success else 'Twilio voice call failed',
            'dose_log_id': dose_log.id
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


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


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Webhook — no JWT required
def whatsapp_webhook(request):
    """
    Webhook handler for patient replies (1, 2, or 3).
    Handles: taken, reschedule +15min, not taking (triggers escalation).
    Implements stale message rejection (> 2 hours).
    Supports Meta verification (GET) and both Meta & Twilio formats (POST).
    """
    import os
    from django.http import HttpResponse

    if request.method == 'GET':
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge')
        
        # Meta webhook verification
        verify_token = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'medimate')
        if mode == 'subscribe' and token == verify_token:
            return HttpResponse(challenge, content_type='text/plain')
        return Response({'error': 'Verification token mismatch or invalid mode'}, status=403)

    # POST payload parsing
    if isinstance(request.data, dict) and 'object' in request.data and request.data.get('object') == 'whatsapp_business_account':
        try:
            entry = request.data.get('entry', [])[0]
            change = entry.get('changes', [])[0]
            value = change.get('value', {})
            message = value.get('messages', [])[0]
            sender_phone = message.get('from', '').replace('+', '').strip()
            body = message.get('text', {}).get('body', '').strip()
        except (IndexError, KeyError, AttributeError):
            return Response({'error': 'Invalid Meta webhook payload structure'}, status=400)
    else:
        # Twilio form data fallback
        sender_phone = request.data.get('From', '').replace('+', '').strip()
        body = request.data.get('Body', '').strip()

    if not sender_phone or not body:
        return Response({'error': 'Sender phone or message body missing'}, status=400)

    # Find latest pending (non-expired) interaction for this phone
    two_hours_ago = timezone.now() - timedelta(hours=2)
    interaction = WhatsAppInteraction.objects.filter(
        whatsapp_number__endswith=sender_phone[-10:],  # match last 10 digits
        status='sent',
        sent_at__gte=two_hours_ago,
    ).order_by('-sent_at').first()

    if not interaction:
        return Response({'error': f'No active interaction found for phone endswith {sender_phone[-10:]} or expired (> 2h)'}, status=404)

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
