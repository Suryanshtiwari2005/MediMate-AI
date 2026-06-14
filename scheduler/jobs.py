import logging
from datetime import date, timedelta
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

logger = logging.getLogger(__name__)

def check_pending_reminders():
    """
    Feature #53: Send WhatsApp reminder for doses > 30 min late.
    Also creates an in-app ChatMessage (is_reminder=True) so reminders appear in the chat.
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

            # Create an in-app chat reminder message
            _create_chat_reminder(dose, variables)

            dose.reminder_sent = True
            dose.save()
            logger.info(f"Background reminder sent for dose {dose.id}")
        except Exception as e:
            logger.error(f"Reminder failed for dose {dose.id}: {e}")


def _create_chat_reminder(dose, ai_variables):
    """Create an in-app ChatMessage for a medication reminder."""
    from apps.chat.models import ChatMessage

    reminder_text = (
        f"💊 Medication Reminder\n\n"
        f"Hi {ai_variables['patient_name']}! It's time for your "
        f"{ai_variables['medicine_name']} ({ai_variables['dosage']}).\n"
        f"Scheduled: {ai_variables['scheduled_time']}\n\n"
        f"{ai_variables.get('ai_personalized_tip', '')}\n\n"
        f"Reply with:\n"
        f"  1 — ✅ Taken\n"
        f"  2 — ⏰ Remind me later\n"
        f"  3 — ❌ Not taking today"
    )

    ChatMessage.objects.create(
        sender=None,  # System message
        recipient=dose.patient.user,
        message=reminder_text,
        is_reminder=True,
        dose_log=dose,
    )
    logger.info(f"In-app chat reminder created for dose {dose.id}")


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


def check_daily_nudges():
    """
    AI Nudge Job: For patients who missed >= 3 doses in the last 7 days,
    generate a personalized nudge message via DeepSeek AI.
    Runs once daily at 9 PM.
    """
    from apps.patients.models import PatientProfile
    from apps.medicines.models import MedicineSchedule
    from apps.doses.models import DoseLog
    from apps.chat.models import ChatMessage
    from services.deepseek_service import generate_ai_nudge

    today = date.today()
    week_ago = today - timedelta(days=7)

    active_patients = PatientProfile.objects.filter(
        user__is_active=True,
    ).select_related('user')

    for patient in active_patients:
        active_schedules = MedicineSchedule.objects.filter(
            patient=patient,
            is_active=True,
        ).select_related('medicine')

        for schedule in active_schedules:
            # Count missed doses for this schedule in the last 7 days
            missed_count = DoseLog.objects.filter(
                schedule=schedule,
                patient=patient,
                scheduled_date__gte=week_ago,
                scheduled_date__lte=today,
                status__in=['missed', 'skipped'],
            ).count()

            if missed_count >= 3:
                try:
                    nudge_text = generate_ai_nudge(
                        patient_name=patient.user.full_name,
                        medicine_name=schedule.medicine.name,
                        dosage=schedule.medicine.dosage,
                        missed_count=missed_count,
                        time_slot=schedule.scheduled_time.strftime("%I:%M %p"),
                    )

                    ChatMessage.objects.create(
                        sender=None,  # System/AI message
                        recipient=patient.user,
                        message=nudge_text,
                        is_ai_nudge=True,
                    )
                    logger.info(
                        f"AI nudge sent to patient {patient.id} for "
                        f"{schedule.medicine.name} (missed {missed_count}/7 days)"
                    )
                except Exception as e:
                    logger.error(
                        f"AI nudge failed for patient {patient.id}, "
                        f"medicine {schedule.medicine.name}: {e}"
                    )


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
    scheduler.add_job(
        check_daily_nudges,
        'cron',
        hour=21,
        minute=0,
        id='daily_ai_nudges',
        replace_existing=True
    )

    scheduler.start()
    logger.info(
        "APScheduler started with jobs: check_reminders, check_escalations, "
        "recalc_risk, daily_ai_nudges"
    )
