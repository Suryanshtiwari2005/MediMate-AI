import os
import django
from datetime import date, time, timedelta
import random

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.patients.models import PatientProfile, Caretaker
from apps.medicines.models import Medicine, MedicineSchedule
from apps.doses.models import DoseLog
from services.ai_service import calculate_risk_score

User = get_user_model()

def seed_data():
    print("--- Cleaning database ---")
    # Delete existing data to start fresh
    DoseLog.objects.all().delete()
    MedicineSchedule.objects.all().delete()
    Medicine.objects.all().delete()
    Caretaker.objects.all().delete()
    PatientProfile.objects.all().delete()
    
    # Keep admin if exists, delete others
    User.objects.exclude(is_superuser=True).delete()

    print("--- Creating users ---")
    # 1. Admin User
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@medimate.ai',
            'full_name': 'Dr. Alok Verma',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    admin_user.set_password('admin123')
    admin_user.save()

    # 2. Caretaker User
    caretaker_user = User.objects.create_user(
        username='caretaker_sharma',
        email='caretaker@example.com',
        password='caretaker123',
        full_name='Ramesh Sharma',
        whatsapp_number='+919302748206',  # Replace with actual number for testing
        role='caretaker'
    )

    # 3. Patient 1 (Adherent patient)
    patient_user1 = User.objects.create_user(
        username='patient_raj',
        email='raj@example.com',
        password='patient123',
        full_name='Rajesh Kumar',
        whatsapp_number='+919301774484',  # Replace with actual number for testing
        role='patient'
    )

    # 4. Patient 2 (Non-adherent patient)
    patient_user2 = User.objects.create_user(
        username='patient_sneha',
        email='sneha@example.com',
        password='patient123',
        full_name='Sneha Patel',
        whatsapp_number='+919999999992',  # Replace with actual number for testing
        role='patient'
    )

    print("--- Creating Patient Profiles & Caretaker ---")
    # Create profiles
    profile1 = PatientProfile.objects.create(
        user=patient_user1,
        age=45,
        gender='male',
        blood_group='O+',
        diseases=['Hypertension'],
        allergies=['Sulfonamides'],
        chronic_conditions=['High Blood Pressure'],
        emergency_phone='+919876543210',
        onboarding_done=True
    )

    profile2 = PatientProfile.objects.create(
        user=patient_user2,
        age=62,
        gender='female',
        blood_group='A-',
        diseases=['Diabetes Type 2', 'Asthma'],
        allergies=['Penicillin'],
        chronic_conditions=['Diabetes'],
        emergency_phone='+919876543210',
        onboarding_done=True
    )

    caretaker = Caretaker.objects.create(
        user=caretaker_user,
        phone='+919876543210',
        is_primary=True
    )
    # Assign both patients to the caretaker
    caretaker.patients.add(profile1, profile2)

    print("--- Creating Medicines & Schedules ---")
    # Medicines
    med_amlodipine = Medicine.objects.create(name='Amlodipine', dosage='5mg', instructions='Take 1 tablet daily in the morning before breakfast')
    med_telmisartan = Medicine.objects.create(name='Telmisartan', dosage='40mg', instructions='Take 1 tablet in the evening after dinner')
    med_metformin = Medicine.objects.create(name='Metformin', dosage='500mg', instructions='Take 1 tablet with meals twice a day')
    med_atorvastatin = Medicine.objects.create(name='Atorvastatin', dosage='10mg', instructions='Take 1 tablet at bedtime')
    med_inhaler = Medicine.objects.create(name='Albuterol Inhaler', dosage='2 puffs', instructions='As needed, or twice daily for asthma prevention')

    # Schedules for Patient 1 (Rajesh Kumar)
    # Start date is 10 days ago so we have history
    start_date_past = date.today() - timedelta(days=10)
    
    sched_raj1 = MedicineSchedule.objects.create(
        patient=profile1,
        medicine=med_amlodipine,
        scheduled_time=time(8, 0),
        start_date=start_date_past,
        is_active=True
    )
    sched_raj2 = MedicineSchedule.objects.create(
        patient=profile1,
        medicine=med_telmisartan,
        scheduled_time=time(20, 30),
        start_date=start_date_past,
        is_active=True
    )

    # Schedules for Patient 2 (Sneha Patel)
    sched_sneha1 = MedicineSchedule.objects.create(
        patient=profile2,
        medicine=med_metformin,
        scheduled_time=time(9, 0),
        start_date=start_date_past,
        is_active=True
    )
    sched_sneha2 = MedicineSchedule.objects.create(
        patient=profile2,
        medicine=med_atorvastatin,
        scheduled_time=time(22, 0),
        start_date=start_date_past,
        is_active=True
    )
    sched_sneha3 = MedicineSchedule.objects.create(
        patient=profile2,
        medicine=med_inhaler,
        scheduled_time=time(14, 0),
        start_date=start_date_past,
        is_active=True
    )

    print("--- Seeding historical Dose Logs ---")
    # Note: Creating schedules automatically fires the signals, generating 30 days of pending logs starting from start_date_past.
    # We will fetch those generated logs and modify their statuses to create a history.
    
    today = date.today()
    
    # Rajesh: Very adherent (90% taken)
    raj_logs = DoseLog.objects.filter(patient=profile1)
    for log in raj_logs:
        # If scheduled in the past
        if log.scheduled_date < today:
            if random.random() < 0.92:
                log.status = 'taken'
                # Taken roughly around scheduled time
                log.taken_at = timezone.make_aware(
                    datetime_from_date_time(log.scheduled_date, log.scheduled_time) + 
                    timedelta(minutes=random.randint(-15, 45))
                )
            else:
                log.status = 'skipped'
                log.skip_reason = 'Felt slightly dizzy, consulted doctor.'
            log.save()
        elif log.scheduled_date == today:
            # If scheduled time has passed
            current_time = timezone.now().time()
            if log.scheduled_time < current_time:
                log.status = 'taken'
                log.taken_at = timezone.now() - timedelta(minutes=10)
                log.save()

    # Sneha: Not very adherent (misses often) to simulate medium/high risk
    sneha_logs = DoseLog.objects.filter(patient=profile2)
    for log in sneha_logs:
        if log.scheduled_date < today:
            rand = random.random()
            if rand < 0.55:
                log.status = 'taken'
                log.taken_at = timezone.make_aware(
                    datetime_from_date_time(log.scheduled_date, log.scheduled_time) + 
                    timedelta(minutes=random.randint(0, 60))
                )
            elif rand < 0.80:
                log.status = 'missed'
                log.missed_at = timezone.make_aware(
                    datetime_from_date_time(log.scheduled_date, log.scheduled_time) + 
                    timedelta(minutes=45)
                )
            else:
                log.status = 'skipped'
                log.skip_reason = 'Forgot to take medicine with me to work.'
            log.save()
        elif log.scheduled_date == today:
            # Let's mark the morning dose as missed to simulate an active escalation scenario
            if log.scheduled_time < time(12, 0):
                log.status = 'missed'
                log.missed_at = timezone.make_aware(
                    datetime_from_date_time(log.scheduled_date, log.scheduled_time) + 
                    timedelta(minutes=45)
                )
                log.escalated = True
                log.save()

    print("--- Recalculating patient risk levels ---")
    # Calculate and save risk scores
    risk_raj = calculate_risk_score(profile1.id)
    profile1.risk_level = risk_raj['level']
    profile1.adherence_score = 100 - risk_raj['factors']['miss_rate_7d']
    profile1.save()

    risk_sneha = calculate_risk_score(profile2.id)
    profile2.risk_level = risk_sneha['level']
    profile2.adherence_score = 100 - risk_sneha['factors']['miss_rate_7d']
    profile2.save()

    print("--- Seeding Complete ---")
    print(f"Rajesh Kumar Adherence Score: {profile1.adherence_score}% (Risk: {profile1.risk_level})")
    print(f"Sneha Patel Adherence Score: {profile2.adherence_score}% (Risk: {profile2.risk_level})")
    print("\nCredentials:")
    print("- Admin: admin / admin123")
    print("- Caretaker: caretaker_sharma / caretaker123")
    print("- Patients: patient_raj / patient123 , patient_sneha / patient123")

def datetime_from_date_time(d, t):
    from datetime import datetime
    return datetime.combine(d, t)

if __name__ == '__main__':
    seed_data()
