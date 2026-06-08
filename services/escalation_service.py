"""
Feature #55: Secondary Caretaker Alert
Feature #57: Emergency Phone Fallback
Feature #58: Escalation Logging

Handles the escalation pipeline:
- Primary caretaker WhatsApp alert
- Secondary caretaker alert (if assigned)
- Emergency phone fallback (if no caretaker)
- All actions logged in EscalationLog
"""
import logging
from services.whatsapp_service import send_whatsapp_message
from apps.escalation.models import EscalationLog

logger = logging.getLogger(__name__)

CARETAKER_ALERT_TEMPLATE = """🚨 MediMate ALERT

Patient: {patient_name}
Missed: {medicine_name} ({dosage})
Scheduled: {scheduled_time}

The patient has indicated they are not taking this dose.
Please check on them immediately.

— MediMateAI Escalation System"""


def trigger_caretaker_alert(dose_log):
    """
    Send WhatsApp alert to assigned caretakers.
    Feature #55: Alerts secondary caretaker if available.
    Feature #57: Falls back to emergency phone if no caretaker assigned.
    Feature #58: Logs every escalation action.
    """
    patient = dose_log.patient
    caretakers = patient.caretakers.all()

    if not caretakers.exists():
        # Feature #57: Fallback to patient's emergency phone
        emergency = patient.emergency_phone
        if emergency:
            msg = _build_alert_message(dose_log)
            success = send_whatsapp_message(emergency, msg)
            _log_escalation(dose_log, patient, 'whatsapp_primary', emergency, msg, success)
            logger.info(f"Emergency fallback alert sent to {emergency}")
        else:
            logger.warning(f"No caretaker or emergency contact for patient {patient.id}")
        return

    # Send to all assigned caretakers (primary first, then secondary)
    for caretaker in caretakers.order_by('-is_primary'):
        phone = caretaker.user.whatsapp_number or caretaker.phone
        if phone:
            msg = _build_alert_message(dose_log)
            success = send_whatsapp_message(phone, msg)
            # Feature #55: Distinguish primary vs secondary
            level = 'whatsapp_primary' if caretaker.is_primary else 'whatsapp_secondary'
            # Feature #58: Log the escalation
            _log_escalation(dose_log, patient, level, phone, msg, success)
            logger.info(f"Caretaker alert ({level}) sent to {phone}: {'✅' if success else '❌'}")

    dose_log.escalated = True
    dose_log.save()


def _build_alert_message(dose_log) -> str:
    """Build the caretaker alert message from template."""
    return CARETAKER_ALERT_TEMPLATE.format(
        patient_name=dose_log.patient.user.full_name,
        medicine_name=dose_log.medicine.name,
        dosage=dose_log.medicine.dosage,
        scheduled_time=dose_log.scheduled_time.strftime("%I:%M %p"),
    )


def _log_escalation(dose_log, patient, level, phone, message, success):
    """Feature #58: Log every escalation action in EscalationLog."""
    EscalationLog.objects.create(
        dose_log=dose_log,
        patient=patient,
        escalation_level=level,
        recipient_phone=phone,
        message_sent=message,
        success=success,
    )
