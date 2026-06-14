"""
DeepSeek AI Integration Service.

Provides functions for:
- Generic DeepSeek chat completions
- Medicine conflict checking
- Patient reply parsing (taken/rescheduled/missed/invalid)
- AI-powered motivational nudge generation
"""
import os
import json
import logging
import httpx

logger = logging.getLogger(__name__)

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"


def call_deepseek(system_prompt: str, user_message: str, temperature=0.7) -> str | None:
    """
    Call DeepSeek chat completions API.

    Args:
        system_prompt: The system-level instruction for the AI.
        user_message: The user's message to send.
        temperature: Sampling temperature (0.0 - 1.0).

    Returns:
        The AI's reply text, or None if the call fails.
    """
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        logger.error("DEEPSEEK_API_KEY not set in environment variables.")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(DEEPSEEK_API_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip()
            logger.info("DeepSeek API call successful.")
            return content
    except httpx.HTTPStatusError as e:
        logger.error(f"DeepSeek API HTTP error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"DeepSeek API call failed: {e}")
        return None


def check_medicine_conflict(
    new_medicine_name: str,
    new_medicine_dosage: str,
    existing_medicines: list[dict],
) -> dict:
    """
    Check if a new medicine conflicts with the patient's existing medicines.

    Args:
        new_medicine_name: Name of the medicine being added.
        new_medicine_dosage: Dosage of the new medicine.
        existing_medicines: List of dicts with 'name' and 'dosage' keys.

    Returns:
        dict: {"safe": bool, "warnings": [{"severity": "major"/"moderate"/"minor", "message": "..."}]}
    """
    default_safe = {"safe": True, "warnings": []}

    if not existing_medicines:
        return default_safe

    existing_list = "\n".join(
        f"- {m['name']} ({m['dosage']})" for m in existing_medicines
    )

    system_prompt = (
        "You are a pharmacology expert AI assistant. Your job is to check for drug interactions "
        "and conflicts between medicines. Check for:\n"
        "1. Same active ingredient (duplicate prescriptions)\n"
        "2. Dangerous drug-drug interactions\n"
        "3. Contraindicated combinations\n"
        "4. Overlapping therapeutic effects that could cause overdose\n\n"
        "You MUST respond with ONLY valid JSON in this exact format, no other text:\n"
        '{"safe": true/false, "warnings": [{"severity": "major"/"moderate"/"minor", "message": "description"}]}\n\n'
        "If the medicine is safe with no conflicts, return: {\"safe\": true, \"warnings\": []}\n"
        "severity levels: major = life-threatening, moderate = clinically significant, minor = minimal risk"
    )

    user_message = (
        f"New medicine being added: {new_medicine_name} ({new_medicine_dosage})\n\n"
        f"Patient's current medicines:\n{existing_list}\n\n"
        "Check for conflicts and interactions."
    )

    response = call_deepseek(system_prompt, user_message, temperature=0.3)
    if not response:
        logger.warning("DeepSeek conflict check returned no response. Defaulting to safe.")
        return default_safe

    try:
        # Strip markdown code fences if present
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

        result = json.loads(cleaned)
        # Validate expected keys
        if "safe" not in result:
            result["safe"] = True
        if "warnings" not in result:
            result["warnings"] = []
        return result
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.warning(f"Failed to parse DeepSeek conflict response: {e}. Raw: {response}")
        return default_safe


def parse_patient_reply(message: str) -> dict:
    """
    Parse a patient's chat reply to classify their medication response.

    Args:
        message: The patient's reply text.

    Returns:
        dict: {"status": "taken"/"rescheduled"/"missed"/"invalid", "reply": "..."}
    """
    default_invalid = {
        "status": "invalid",
        "reply": "I didn't quite catch that! 😊 Please reply with:\n  1 — ✅ Taken\n  2 — ⏰ Reschedule\n  3 — ❌ Not taking today",
    }

    system_prompt = (
        "You are a medication tracking assistant. Your ONLY job is to classify the patient's reply "
        "about whether they took their medication.\n\n"
        "CLASSIFICATION RULES:\n"
        "- If the patient says they took it, replied '1', 'yes', 'done', 'taken', or similar affirmative → status: 'taken'\n"
        "- If the patient asks to reschedule, replied '2', 'later', 'remind me later', 'snooze', or similar → status: 'rescheduled'\n"
        "- If the patient says they won't take it, replied '3', 'no', 'skip', 'not taking', or similar → status: 'missed'\n"
        "- If the message is ANYTHING else (jokes, questions, unrelated topics, greetings, etc.) → status: 'invalid'\n\n"
        "For 'taken': reply with a brief encouraging message (e.g., 'Great job! 💪')\n"
        "For 'rescheduled': reply confirming you'll remind them later (e.g., 'No worries, I\\'ll remind you again soon! ⏰')\n"
        "For 'missed': reply with understanding but gentle encouragement (e.g., 'That\\'s okay, try not to miss the next one! 💛')\n"
        "For 'invalid': reply politely asking them to respond with the given options:\n"
        "  '1 — ✅ Taken\\n  2 — ⏰ Reschedule\\n  3 — ❌ Not taking today'\n\n"
        "You MUST respond with ONLY valid JSON in this exact format, no other text:\n"
        '{"status": "taken"/"rescheduled"/"missed"/"invalid", "reply": "your message here"}'
    )

    user_message = f"Patient replied: {message}"

    response = call_deepseek(system_prompt, user_message, temperature=0.3)
    if not response:
        logger.warning("DeepSeek parse reply returned no response. Defaulting to invalid.")
        return default_invalid

    try:
        # Strip markdown code fences if present
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

        result = json.loads(cleaned)
        # Validate expected keys
        if result.get("status") not in ("taken", "rescheduled", "missed", "invalid"):
            return default_invalid
        if "reply" not in result:
            result["reply"] = "Thanks for your response!"
        return result
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.warning(f"Failed to parse DeepSeek reply response: {e}. Raw: {response}")
        return default_invalid


def generate_ai_nudge(
    patient_name: str,
    medicine_name: str,
    dosage: str,
    missed_count: int,
    time_slot: str,
) -> str:
    """
    Generate a friendly, personalized nudge message for a patient who has been missing doses.

    Args:
        patient_name: The patient's display name.
        medicine_name: Name of the medicine being missed.
        dosage: Dosage info for the medicine.
        missed_count: Number of times missed in the last 7 days.
        time_slot: The scheduled time for the dose.

    Returns:
        str: A friendly 2-3 sentence nudge message.
    """
    fallback = (
        f"Hey {patient_name}! 👋 Just a gentle nudge — you've missed your "
        f"{medicine_name} a few times recently. Let's get back on track together! 💪"
    )

    system_prompt = (
        "You are a caring, friendly wellness buddy (NOT a doctor). Your tone is warm, "
        "encouraging, and chill — like a good friend checking in.\n\n"
        "RULES:\n"
        "- Keep the message to 2-3 sentences MAX\n"
        "- Be encouraging, NOT preachy or clinical\n"
        "- Use 1-2 emojis naturally\n"
        "- Address the patient by their first name\n"
        "- Don't give medical advice, just motivate\n"
        "- Make it feel personal, not robotic\n"
        "- Respond with ONLY the nudge message text, nothing else"
    )

    user_message = (
        f"Patient name: {patient_name}\n"
        f"Medicine: {medicine_name} ({dosage})\n"
        f"Missed {missed_count} times in the last 7 days\n"
        f"Usual time: {time_slot}\n\n"
        "Generate a friendly nudge message."
    )

    response = call_deepseek(system_prompt, user_message, temperature=0.8)
    if not response:
        logger.warning("DeepSeek nudge generation failed. Using fallback message.")
        return fallback

    # Clean up any quotes the model might wrap around the message
    cleaned = response.strip().strip('"').strip("'")
    return cleaned if cleaned else fallback
