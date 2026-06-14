import logging
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import ChatMessage
from .serializers import ChatMessageSerializer

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request):
    """
    GET /api/chat/messages/
    Retrieve chat messages for the authenticated user.

    Query params:
        - patient_id: Filter conversation by patient profile ID
        - user_id: Filter conversation by user ID
    """
    user = request.user
    patient_id = request.GET.get('patient_id')
    user_id = request.GET.get('user_id')
    other_user_id = None

    if patient_id:
        # Look up the PatientProfile to get the associated user
        from apps.patients.models import PatientProfile
        try:
            patient_profile = PatientProfile.objects.get(id=patient_id)
            other_user_id = patient_profile.user_id
        except PatientProfile.DoesNotExist:
            return Response(
                {'error': 'Patient not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
    elif user_id:
        other_user_id = int(user_id)

    if other_user_id:
        # Messages between request.user and the other user (both directions)
        # Also include system messages (sender=None) to the current user
        messages = ChatMessage.objects.filter(
            Q(sender=user, recipient_id=other_user_id) |
            Q(sender_id=other_user_id, recipient=user) |
            Q(sender__isnull=True, recipient=user)
        ).order_by('created_at')
    else:
        # All messages where request.user is sender or recipient
        messages = ChatMessage.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).order_by('created_at')

    # Mark unread messages addressed to request.user as read
    unread = messages.filter(recipient=user, is_read=False)
    unread.update(is_read=True)

    return Response({
        'messages': ChatMessageSerializer(messages, many=True).data,
        'count': messages.count(),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    """
    POST /api/chat/send/
    Send a chat message.

    Body params:
        - recipient_id OR patient_id: Who to send the message to
        - message: The message text
    """
    user = request.user
    recipient_id = request.data.get('recipient_id')
    patient_id = request.data.get('patient_id')
    message_text = request.data.get('message', '').strip()

    if not message_text:
        return Response(
            {'error': 'Message text is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Resolve recipient
    if not recipient_id and not patient_id and user.role == 'patient':
        try:
            caretaker = user.patient_profile.caretakers.first()
            if caretaker:
                recipient_id = caretaker.user_id
        except Exception:
            pass

    if patient_id and not recipient_id:
        from apps.patients.models import PatientProfile
        try:
            patient_profile = PatientProfile.objects.get(id=patient_id)
            recipient_id = patient_profile.user_id
        except PatientProfile.DoesNotExist:
            return Response(
                {'error': 'Patient not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

    if not recipient_id:
        return Response(
            {'error': 'recipient_id or patient_id is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    from apps.users.models import User
    try:
        recipient = User.objects.get(id=recipient_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'Recipient user not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Create the chat message
    chat_msg = ChatMessage.objects.create(
        sender=user,
        recipient=recipient,
        message=message_text,
    )

    # If the sender is a patient replying, check for pending reminder messages
    if user.role == 'patient':
        _process_patient_reply(user, message_text)

    return Response(
        ChatMessageSerializer(chat_msg).data,
        status=status.HTTP_201_CREATED,
    )


def _process_patient_reply(patient_user, message_text):
    """
    Process a patient's reply to a reminder message using DeepSeek AI.
    Finds the latest unresponded reminder, parses the reply, updates the DoseLog,
    and sends an AI reply back.
    """
    from services.deepseek_service import parse_patient_reply

    # Find the latest unresponded reminder for this patient
    latest_reminder = ChatMessage.objects.filter(
        recipient=patient_user,
        is_reminder=True,
        dose_log__isnull=False,
    ).order_by('-created_at').first()

    if not latest_reminder or not latest_reminder.dose_log:
        return

    dose_log = latest_reminder.dose_log

    # Skip if dose is already resolved
    if dose_log.status != 'pending':
        return

    # Parse the patient's reply via DeepSeek
    try:
        parsed = parse_patient_reply(message_text)
    except Exception as e:
        logger.error(f"Failed to parse patient reply: {e}")
        return

    ai_status = parsed.get('status', 'invalid')
    ai_reply = parsed.get('reply', 'Thanks for your response!')

    # Update the DoseLog based on the parsed status
    if ai_status == 'taken':
        dose_log.status = 'taken'
        dose_log.taken_at = timezone.now()
        dose_log.save()
    elif ai_status == 'rescheduled':
        dose_log.status = 'rescheduled'
        dose_log.save()
    elif ai_status == 'missed':
        dose_log.status = 'missed'
        dose_log.missed_at = timezone.now()
        dose_log.save()
    # 'invalid' → no DoseLog update

    # Create an AI reply message back to the patient
    ChatMessage.objects.create(
        sender=None,  # System/AI message
        recipient=patient_user,
        message=ai_reply,
        is_ai_nudge=True,
        dose_log=dose_log if ai_status != 'invalid' else None,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_count(request):
    """
    GET /api/chat/unread-count/
    Returns the count of unread messages for the authenticated user.
    """
    count = ChatMessage.objects.filter(
        recipient=request.user,
        is_read=False,
    ).count()

    return Response({'count': count})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_medicine_conflict_view(request):
    """
    POST /api/chat/check-conflict/
    Check if a medicine conflicts with the patient's existing medicines.

    Body params:
        - medicine_id: ID of the medicine being added
    """
    from apps.medicines.models import Medicine, MedicineSchedule
    from services.deepseek_service import check_medicine_conflict

    medicine_id = request.data.get('medicine_id')
    if not medicine_id:
        return Response(
            {'error': 'medicine_id is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        new_medicine = Medicine.objects.get(id=medicine_id)
    except Medicine.DoesNotExist:
        return Response(
            {'error': 'Medicine not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Get the patient's existing active medicine schedules
    user = request.user
    try:
        patient_profile = user.patient_profile
    except Exception:
        return Response(
            {'error': 'No patient profile found for this user.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    active_schedules = MedicineSchedule.objects.filter(
        patient=patient_profile,
        is_active=True,
    ).select_related('medicine')

    existing_medicines = [
        {'name': sched.medicine.name, 'dosage': sched.medicine.dosage}
        for sched in active_schedules
        if sched.medicine_id != new_medicine.id
    ]

    result = check_medicine_conflict(
        new_medicine_name=new_medicine.name,
        new_medicine_dosage=new_medicine.dosage,
        existing_medicines=existing_medicines,
    )

    return Response(result)
