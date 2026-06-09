import os
import logging
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from apps.escalation.models import EscalationLog

logger = logging.getLogger(__name__)

def make_bot_call(dose_log):
    """
    Feature #56: Automated Twilio voice call reads alert message to caretaker's phone.
    Returns:
        bool: True if call successfully placed/simulated, False otherwise.
    """
    patient = dose_log.patient
    caretaker = patient.caretakers.filter(is_primary=True).first()
    
    # If no caretaker, fallback to emergency phone of the patient
    if not caretaker:
        phone = patient.emergency_phone
        recipient_name = "Emergency Contact"
    else:
        phone = caretaker.user.whatsapp_number or caretaker.phone
        recipient_name = caretaker.user.full_name

    if not phone:
        logger.warning(f"No phone number available for voice call (Patient #{patient.id})")
        return False

    # Ensure phone number formatting has '+'
    phone_str = str(phone).strip()
    if not phone_str.startswith('+'):
        phone_str = '+' + phone_str

    sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
    token = os.environ.get('TWILIO_AUTH_TOKEN', '')
    from_phone = os.environ.get('TWILIO_PHONE', '')

    if not all([sid, token, from_phone]):
        logger.warning("Twilio credentials not set — simulating voice call")
        # Log as attempted even if simulated
        dose_log.call_attempted = True
        dose_log.save()
        _log_call(dose_log, patient, phone_str, f"SIMULATED Voice Call to {recipient_name} — Twilio credentials not set.", True)
        return True

    twiml = VoiceResponse()
    twiml.say(
        f"Alert from MediMate. Patient {patient.user.full_name} has missed their "
        f"{dose_log.medicine.name} medication scheduled for "
        f"{dose_log.scheduled_time.strftime('%I:%M %p')}. "
        f"Please contact them immediately. This is an automated alert.",
        voice='alice',
    )

    try:
        client = Client(sid, token)
        call = client.calls.create(
            twiml=str(twiml),
            to=phone_str,
            from_=from_phone,
        )
        dose_log.call_attempted = True
        dose_log.save()
        _log_call(dose_log, patient, phone_str, f"Call SID: {call.sid}", True)
        return True
    except Exception as e:
        logger.error(f"Bot call failed to {phone_str}: {e}")
        _log_call(dose_log, patient, phone_str, str(e), False)
        dose_log.call_attempted = True
        dose_log.save()
        return False


def _log_call(dose_log, patient, phone, message, success):
    EscalationLog.objects.create(
        dose_log=dose_log,
        patient=patient,
        escalation_level='bot_call',
        recipient_phone=phone,
        message_sent=message,
        success=success,
    )
