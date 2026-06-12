"""
Feature #35: Meta WhatsApp Cloud API Integration
Feature #36: Interactive Button Template
Feature #43: WhatsApp Interaction Log

Sends WhatsApp messages via official WhatsApp Cloud API and logs all interactions.
"""
import httpx
import os
import logging

logger = logging.getLogger(__name__)

# Feature #36: Interactive Button Template with 1/2/3 reply options
REMINDER_TEMPLATE = """💊 MediMate Reminder — {patient_name}

It's time for your {medicine_name} ({dosage}).
Scheduled: {scheduled_time}

{ai_personalized_tip}

{streak}

Reply with:
  *1* — ✅ Taken
  *2* — ⏰ Remind me in 15 minutes
  *3* — ❌ Not taking today"""


def send_whatsapp_message(phone: str, message: str) -> bool:
    """
    Feature #35: Send a WhatsApp message via official WhatsApp Cloud API.
    Returns True if sent successfully, False otherwise.
    """
    phone_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN', '')
    
    if not phone_id or not access_token:
        logger.warning("WHATSAPP_PHONE_NUMBER_ID or WHATSAPP_ACCESS_TOKEN not set — skipping WhatsApp send")
        return False

    # Clean phone number: keep only digits
    clean_phone = "".join(c for c in str(phone) if c.isdigit())
    if not clean_phone:
        logger.error("Empty phone number after cleaning")
        return False

    url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": clean_phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message
        }
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            logger.info(f"WhatsApp API response: {resp.status_code} - {resp.text}")
            resp.raise_for_status()
            logger.info(f"WhatsApp sent to {clean_phone}: {resp.status_code}")
            return True
    except httpx.HTTPStatusError as e:
        logger.error(f"WhatsApp send error (HTTP {e.response.status_code}): {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        return False


def send_reminder(dose_log, patient, ai_variables: dict) -> bool:
    """
    Build and send interactive reminder using the template.
    Feature #43: Logs the interaction in WhatsAppInteraction table.
    """
    message = REMINDER_TEMPLATE.format(**ai_variables)
    phone = patient.user.whatsapp_number
    if not phone:
        logger.warning(f"No WhatsApp number for patient {patient.id}")
        return False

    success = send_whatsapp_message(phone, message)

    # Feature #43: Log the interaction
    from apps.whatsapp.models import WhatsAppInteraction
    WhatsAppInteraction.objects.create(
        dose_log=dose_log,
        patient=patient,
        whatsapp_number=phone,
        message_sent=message,
        ai_variables=ai_variables,
        status='sent' if success else 'failed',
    )
    return success
