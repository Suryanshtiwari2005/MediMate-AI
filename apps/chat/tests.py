from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from datetime import date, time

from apps.chat.models import ChatMessage
from apps.patients.models import PatientProfile, Caretaker
from apps.medicines.models import Medicine, MedicineSchedule
from apps.doses.models import DoseLog
from services import deepseek_service

User = get_user_model()


class DeepSeekServiceTests(APITestCase):
    """Test cases for DeepSeek helper functions in deepseek_service.py."""

    @patch("services.deepseek_service.call_deepseek")
    def test_check_medicine_conflict_safe(self, mock_call):
        # Mock DeepSeek to return a safe json response
        mock_call.return_value = '{"safe": true, "warnings": []}'
        
        result = deepseek_service.check_medicine_conflict(
            new_medicine_name="Aspirin",
            new_medicine_dosage="100mg",
            existing_medicines=[{"name": "Paracetamol", "dosage": "500mg"}]
        )
        self.assertTrue(result["safe"])
        self.assertEqual(len(result["warnings"]), 0)

    @patch("services.deepseek_service.call_deepseek")
    def test_check_medicine_conflict_unsafe(self, mock_call):
        # Mock DeepSeek to return an interaction warning
        mock_call.return_value = (
            '{"safe": false, "warnings": [{"severity": "major", "message": "High risk of bleeding."}]}'
        )
        
        result = deepseek_service.check_medicine_conflict(
            new_medicine_name="Warfarin",
            new_medicine_dosage="5mg",
            existing_medicines=[{"name": "Aspirin", "dosage": "100mg"}]
        )
        self.assertFalse(result["safe"])
        self.assertEqual(result["warnings"][0]["severity"], "major")
        self.assertEqual(result["warnings"][0]["message"], "High risk of bleeding.")

    @patch("services.deepseek_service.call_deepseek")
    def test_parse_patient_reply_taken(self, mock_call):
        mock_call.return_value = '{"status": "taken", "reply": "Awesome! 💪"}'
        result = deepseek_service.parse_patient_reply("I took my dose")
        self.assertEqual(result["status"], "taken")
        self.assertEqual(result["reply"], "Awesome! 💪")

    @patch("services.deepseek_service.call_deepseek")
    def test_generate_ai_nudge(self, mock_call):
        mock_call.return_value = "Hey John! Remember to stay on track and take your meds today! 😊"
        nudge = deepseek_service.generate_ai_nudge("John", "Metformin", "500mg", 3, "Morning")
        self.assertEqual(nudge, "Hey John! Remember to stay on track and take your meds today! 😊")


class ChatAPITests(APITestCase):
    """Test cases for chat app View and URL endpoints."""

    def setUp(self):
        # Create users
        self.patient_user = User.objects.create_user(
            username="patient",
            email="patient@test.com",
            password="testpassword123",
            role="patient",
            full_name="Rajesh Patient"
        )
        self.caretaker_user = User.objects.create_user(
            username="caretaker",
            email="caretaker@test.com",
            password="testpassword123",
            role="caretaker",
            full_name="Anil Caretaker"
        )

        # Create patient profile
        self.patient_profile = PatientProfile.objects.create(
            user=self.patient_user,
            age=45,
            gender="male"
        )

        # Create caretaker profile and link patient
        self.caretaker_profile = Caretaker.objects.create(
            user=self.caretaker_user,
            phone="1234567890",
            is_primary=True
        )
        self.caretaker_profile.patients.add(self.patient_profile)

        # Create medicine and dose log for testing replies
        self.medicine = Medicine.objects.create(name="Amlodipine", dosage="5mg")
        self.schedule = MedicineSchedule.objects.create(
            patient=self.patient_profile,
            medicine=self.medicine,
            scheduled_time=time(18, 0),
            start_date=date(2026, 6, 1)
        )
        self.dose_log = DoseLog.objects.filter(
            schedule=self.schedule,
            scheduled_date=date(2026, 6, 14),
            scheduled_time=time(18, 0)
        ).first()
        if not self.dose_log:
            self.dose_log = DoseLog.objects.create(
                schedule=self.schedule,
                patient=self.patient_profile,
                medicine=self.medicine,
                scheduled_date=date(2026, 6, 14),
                scheduled_time=time(18, 0),
                status="pending"
            )
        else:
            self.dose_log.status = "pending"
            self.dose_log.save()

    def test_get_messages_unauthenticated(self):
        url = reverse("chat-messages")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_send_and_get_messages(self):
        # Authenticate as caretaker
        self.client.force_authenticate(user=self.caretaker_user)
        
        # Send message
        send_url = reverse("chat-send")
        send_data = {
            "recipient_id": self.patient_user.id,
            "message": "Hello Rajesh, did you take your morning pill?"
        }
        send_response = self.client.post(send_url, send_data)
        self.assertEqual(send_response.status_code, status.HTTP_201_CREATED)
        
        # Authenticate as patient and fetch messages
        self.client.force_authenticate(user=self.patient_user)
        messages_url = reverse("chat-messages")
        get_response = self.client.get(messages_url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        
        # Verify message count and content
        messages_list = get_response.data["messages"]
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0]["message"], "Hello Rajesh, did you take your morning pill?")
        self.assertEqual(messages_list[0]["sender"], self.caretaker_user.id)

    @patch("services.deepseek_service.parse_patient_reply")
    def test_patient_reply_to_reminder(self, mock_parse_reply):
        # Create an in-app reminder ChatMessage for the patient
        reminder_msg = ChatMessage.objects.create(
            sender=None,
            recipient=self.patient_user,
            message="It's time to take your Amlodipine!",
            is_reminder=True,
            dose_log=self.dose_log
        )

        # Mock DeepSeek to parse patient reply as "taken"
        mock_parse_reply.return_value = {"status": "taken", "reply": "Great job! 💪"}

        # Authenticate as patient
        self.client.force_authenticate(user=self.patient_user)

        # Send a reply message
        send_url = reverse("chat-send")
        send_data = {
            "message": "done"
        }
        response = self.client.post(send_url, send_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that DoseLog was updated to taken
        self.dose_log.refresh_from_db()
        self.assertEqual(self.dose_log.status, "taken")

        # Check that an AI response ChatMessage was created
        messages = ChatMessage.objects.filter(recipient=self.patient_user).order_by("created_at")
        # should have reminder, patient's reply (which goes from patient to caretaker or just saved), and the AI reply
        # Wait, the views.py might also send messages. Let's make sure
        ai_replies = messages.filter(sender__isnull=True, is_ai_nudge=True)
        self.assertTrue(ai_replies.exists())
        self.assertEqual(ai_replies.first().message, "Great job! 💪")

    def test_get_unread_count(self):
        # Create 2 unread messages from caretaker to patient
        ChatMessage.objects.create(sender=self.caretaker_user, recipient=self.patient_user, message="Msg 1")
        ChatMessage.objects.create(sender=self.caretaker_user, recipient=self.patient_user, message="Msg 2")

        # Authenticate as patient
        self.client.force_authenticate(user=self.patient_user)
        unread_url = reverse("chat-unread-count")
        response = self.client.get(unread_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        # Fetch messages to mark them as read
        messages_url = reverse("chat-messages")
        self.client.get(messages_url)

        # Verify unread count is now 0
        response = self.client.get(unread_url)
        self.assertEqual(response.data["count"], 0)

    @patch("services.deepseek_service.check_medicine_conflict")
    def test_check_medicine_conflict_view(self, mock_check_conflict):
        mock_check_conflict.return_value = {"safe": True, "warnings": []}

        # Create another medicine to check against
        new_medicine = Medicine.objects.create(name="Metformin", dosage="500mg")

        # Authenticate as patient
        self.client.force_authenticate(user=self.patient_user)
        conflict_url = reverse("chat-check-conflict")
        response = self.client.post(conflict_url, {"medicine_id": new_medicine.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["safe"])
