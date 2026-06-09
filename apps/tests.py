from datetime import date, time, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from apps.patients.models import PatientProfile, Caretaker
from apps.medicines.models import Medicine, MedicineSchedule
from apps.doses.models import DoseLog
from apps.whatsapp.models import WhatsAppInteraction
from apps.escalation.models import EscalationLog
from services.ai_service import calculate_risk_score
from services.ai_message_service import generate_ai_variables

User = get_user_model()

class MediMateTests(APITestCase):
    def setUp(self):
        # Create users
        self.patient_user = User.objects.create_user(
            username='patient1',
            email='patient1@example.com',
            password='password123',
            full_name='John Doe',
            whatsapp_number='1234567890',
            role='patient'
        )
        self.caretaker_user = User.objects.create_user(
            username='caretaker1',
            email='caretaker1@example.com',
            password='password123',
            full_name='Jane Caretaker',
            whatsapp_number='0987654321',
            role='caretaker'
        )
        
        # Create profiles
        self.patient_profile = PatientProfile.objects.create(
            user=self.patient_user,
            age=30,
            gender='male',
            emergency_phone='5551234567'
        )
        self.caretaker_profile = Caretaker.objects.create(
            user=self.caretaker_user,
            phone='0987654321',
            is_primary=True
        )
        self.caretaker_profile.patients.add(self.patient_profile)

        # Create medicine
        self.medicine = Medicine.objects.create(
            name='Aspirin',
            dosage='100mg',
            instructions='Take after lunch'
        )

    def test_dose_log_auto_generated(self):
        """Feature #19: Auto Dose Log Generation (post_save signal)."""
        schedule = MedicineSchedule.objects.create(
            patient=self.patient_profile,
            medicine=self.medicine,
            scheduled_time=time(14, 0),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            is_active=True
        )
        # Should generate 6 DoseLog entries (start_date to end_date inclusive)
        logs = DoseLog.objects.filter(schedule=schedule)
        self.assertEqual(logs.count(), 6)

    def test_duplicate_taken_rejected(self):
        """Feature #26: Returns 409 Conflict if dose is already marked as taken."""
        schedule = MedicineSchedule.objects.create(
            patient=self.patient_profile,
            medicine=self.medicine,
            scheduled_time=time(14, 0),
            start_date=date.today(),
            is_active=True
        )
        dose = DoseLog.objects.filter(schedule=schedule).first()
        
        # Authenticate client with JWT
        refresh = RefreshToken.for_user(self.patient_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # First take should succeed
        resp1 = self.client.post(f'/api/doses/{dose.id}/take/')
        self.assertEqual(resp1.status_code, 200)
        
        # Second take should return 409
        resp2 = self.client.post(f'/api/doses/{dose.id}/take/')
        self.assertEqual(resp2.status_code, 409)

    def test_webhook_reply_1_marks_taken(self):
        """Feature #39: Webhook Reply Handler - '1' marks taken."""
        schedule = MedicineSchedule.objects.create(
            patient=self.patient_profile,
            medicine=self.medicine,
            scheduled_time=time(14, 0),
            start_date=date.today(),
            is_active=True
        )
        dose = DoseLog.objects.filter(schedule=schedule).first()
        
        # Create initial interaction
        interaction = WhatsAppInteraction.objects.create(
            dose_log=dose,
            patient=self.patient_profile,
            whatsapp_number='1234567890',
            message_sent='Reminder text',
            status='sent'
        )
        
        # Simulate webhook POST
        resp = self.client.post('/api/whatsapp/webhook/', {
            'From': '+1234567890',
            'Body': '1'
        })
        self.assertEqual(resp.status_code, 200)
        
        # Refresh dose status
        dose.refresh_from_db()
        self.assertEqual(dose.status, 'taken')
        
        interaction.refresh_from_db()
        self.assertEqual(interaction.status, 'responded')
        self.assertEqual(interaction.response_received, '1')

    def test_webhook_reply_2_reschedules(self):
        """Feature #40: Webhook Reply Handler - '2' reschedules +15 min."""
        schedule = MedicineSchedule.objects.create(
            patient=self.patient_profile,
            medicine=self.medicine,
            scheduled_time=time(14, 0),
            start_date=date.today(),
            is_active=True
        )
        dose = DoseLog.objects.filter(schedule=schedule).first()
        
        interaction = WhatsAppInteraction.objects.create(
            dose_log=dose,
            patient=self.patient_profile,
            whatsapp_number='1234567890',
            message_sent='Reminder text',
            status='sent'
        )
        
        resp = self.client.post('/api/whatsapp/webhook/', {
            'From': '+1234567890',
            'Body': '2'
        })
        self.assertEqual(resp.status_code, 200)
        
        dose.refresh_from_db()
        self.assertEqual(dose.status, 'rescheduled')
        
        # A new DoseLog should be created for this patient +15 min from now
        new_doses = DoseLog.objects.filter(patient=self.patient_profile, status='pending')
        self.assertTrue(new_doses.exists())

    def test_webhook_reply_3_triggers_escalation(self):
        """Feature #41: Webhook Reply Handler - '3' triggers caretaker alert."""
        schedule = MedicineSchedule.objects.create(
            patient=self.patient_profile,
            medicine=self.medicine,
            scheduled_time=time(14, 0),
            start_date=date.today(),
            is_active=True
        )
        dose = DoseLog.objects.filter(schedule=schedule).first()
        
        interaction = WhatsAppInteraction.objects.create(
            dose_log=dose,
            patient=self.patient_profile,
            whatsapp_number='1234567890',
            message_sent='Reminder text',
            status='sent'
        )
        
        resp = self.client.post('/api/whatsapp/webhook/', {
            'From': '+1234567890',
            'Body': '3'
        })
        self.assertEqual(resp.status_code, 200)
        
        dose.refresh_from_db()
        self.assertEqual(dose.status, 'missed')
        self.assertTrue(dose.escalated)
        
        # Escalation Log should be created
        escalations = EscalationLog.objects.filter(dose_log=dose)
        self.assertTrue(escalations.exists())
        self.assertEqual(escalations.first().recipient_phone, '0987654321') # Caretaker phone

    def test_risk_score_formula(self):
        """Feature #45: Test risk scoring formula calculations."""
        schedule = MedicineSchedule.objects.create(
            patient=self.patient_profile,
            medicine=self.medicine,
            scheduled_time=time(14, 0),
            start_date=date.today() - timedelta(days=5),
            is_active=True
        )
        
        # Mark all past 5 doses as missed to simulate high-risk behavior
        DoseLog.objects.filter(schedule=schedule).update(status='missed')
        
        risk = calculate_risk_score(self.patient_profile.id)
        self.assertGreaterEqual(risk['score'], 50)
        self.assertEqual(risk['level'], 'high' if risk['score'] < 75 else 'critical')

    def test_ai_variable_generation(self):
        """Feature #37: AI Motivational variables generation structure."""
        schedule = MedicineSchedule.objects.create(
            patient=self.patient_profile,
            medicine=self.medicine,
            scheduled_time=time(14, 0),
            start_date=date.today(),
            is_active=True
        )
        dose = DoseLog.objects.filter(schedule=schedule).first()
        
        variables = generate_ai_variables(self.patient_profile, dose)
        self.assertEqual(variables['patient_name'], 'John Doe')
        self.assertEqual(variables['medicine_name'], 'Aspirin')
        self.assertIn('streak', variables)
        self.assertIn('ai_personalized_tip', variables)
