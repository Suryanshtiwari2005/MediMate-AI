import logging
from datetime import date, timedelta
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

logger = logging.getLogger(__name__)

def check_pending_reminders():
    """
    Feature #53: Send WhatsApp reminder for doses > 30 min late.
    Runs every 1 minute.
    """
    from apps.doses.models import DoseLog
    from services.ai_message_service import generate_ai_variables
    from services.whatsapp_service import send_reminder

    now = timezone.now()
    cutoff_time = (now - timedelta(minutes=30)).time()
    today = date.today()

    overdue = DoseLog.objects.filter(
        scheduled_date=today,
        status='pending',
        reminder_sent=False,
        scheduled_time__lte=cutoff_time,
    ).select_related('patient', 'patient__user', 'medicine')

    for dose in overdue:
        try:
            variables = generate_ai_variables(dose.patient, dose)
            send_reminder(dose, dose.patient, variables)
            dose.reminder_sent = True
            dose.save()
            logger.info(f"Background reminder sent for dose {dose.id}")
        except Exception as e:
            logger.error(f"Reminder failed for dose {dose.id}: {e}")


def check_escalations():
    """
    Feature #54: Escalate doses > 45min late (WhatsApp caretaker).
    Feature #56: Bot voice call to caretaker at T+75min.
    Runs every 1 minute.
    """
    from apps.doses.models import DoseLog
    from services.escalation_service import trigger_caretaker_alert
    from services.call_service import make_bot_call

    now = timezone.now()
    cutoff_45 = (now - timedelta(minutes=45)).time()
    cutoff_75 = (now - timedelta(minutes=75)).time()
    today = date.today()

    # 1. Primary/Secondary Caretaker WhatsApp Alert at T+45
    needs_escalation = DoseLog.objects.filter(
        scheduled_date=today,
        status__in=['pending', 'missed'],
        escalated=False,
        scheduled_time__lte=cutoff_45,
    ).select_related('patient', 'medicine')

    for dose in needs_escalation:
        try:
            trigger_caretaker_alert(dose)
            logger.info(f"Escalated dose {dose.id} via WhatsApp")
        except Exception as e:
            logger.error(f"Escalation failed for dose {dose.id}: {e}")

    # 2. Automated Voice Call Alert to Caretaker at T+75
    needs_voice_escalation = DoseLog.objects.filter(
        scheduled_date=today,
        status__in=['pending', 'missed'],
        call_attempted=False,
        scheduled_time__lte=cutoff_75,
    ).select_related('patient', 'medicine')

    for dose in needs_voice_escalation:
        try:
            make_bot_call(dose)
            logger.info(f"Escalated dose {dose.id} via Bot Call")
        except Exception as e:
            logger.error(f"Bot Call failed for dose {dose.id}: {e}")


def recalculate_risk_scores():
    """
    Feature #70: Recalculate risk scores for all active patients.
    Runs every 6 hours.
    """
    from apps.patients.models import PatientProfile
    from services.ai_service import calculate_risk_score

    for patient in PatientProfile.objects.filter(user__is_active=True):
        try:
            result = calculate_risk_score(patient.id)
            patient.risk_level = result['level']
            # Also update the adherence score if needed, but risk level is primary
            patient.save()
            logger.info(f"Recalculated risk score for patient {patient.id}: {patient.risk_level}")
        except Exception as e:
            logger.error(f"Risk calculation failed for patient {patient.id}: {e}")


def start_scheduler():
    """Start the background task scheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    # Add jobs
    scheduler.add_job(
        check_pending_reminders, 
        'interval', 
        minutes=1, 
        id='check_reminders',
        replace_existing=True
    )
    scheduler.add_job(
        check_escalations, 
        'interval', 
        minutes=1, 
        id='check_escalations',
        replace_existing=True
    )
    scheduler.add_job(
        recalculate_risk_scores, 
        'interval', 
        hours=6, 
        id='recalc_risk',
        replace_existing=True
    )

    scheduler.start()
    logger.info("APScheduler started with jobs: check_reminders, check_escalations, recalc_risk")
