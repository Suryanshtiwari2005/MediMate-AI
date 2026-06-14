"""
Feature #35: CallMeBot Integration
Feature #36: Interactive Button Template
Feature #43: WhatsApp Interaction Log

Sends WhatsApp messages via CallMeBot free gateway and logs all interactions.
"""
import httpx
import urllib.parse
import os
import logging

logger = logging.getLogger(__name__)

CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"

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
    Sends a WhatsApp message.
    - If WHATSAPP_ACCESS_TOKEN is set, it uses the official Meta WhatsApp Cloud API.
    - Else if CALLMEBOT_APIKEY is set, it uses the CallMeBot free gateway.
    - Otherwise, it logs a simulation warning and returns False.
    """
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN', '')
    phone_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')
    
    # Format phone number for Meta (only digits, e.g. "919999999999")
    clean_phone = ''.join(c for c in str(phone) if c.isdigit())

    if access_token and phone_id:
        url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
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
                if resp.status_code in (200, 201):
                    logger.info(f"Official WhatsApp sent to {phone}: {resp.status_code}")
                    return True
                else:
                    logger.error(f"Official WhatsApp send failed: {resp.status_code} - {resp.text}")
                    return False
        except Exception as e:
            logger.error(f"Official WhatsApp send exception: {e}")
            return False

    # Fallback to CallMeBot
    apikey = os.environ.get('CALLMEBOT_APIKEY', '')
    if apikey:
        params = {
            'phone': phone,
            'text': message,
            'apikey': apikey,
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(CALLMEBOT_URL, params=params)
                resp.raise_for_status()
                logger.info(f"CallMeBot WhatsApp sent to {phone}: {resp.status_code}")
                return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning("CallMeBot rate limited (429). Will retry in 60s.")
            else:
                logger.error(f"CallMeBot WhatsApp send error: {e}")
            return False
        except Exception as e:
            logger.error(f"CallMeBot WhatsApp send failed: {e}")
            return False

    logger.warning(f"No WhatsApp API credentials configured (WHATSAPP_ACCESS_TOKEN or CALLMEBOT_APIKEY). Simulated send to {phone}.")
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
