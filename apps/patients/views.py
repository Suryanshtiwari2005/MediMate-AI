from datetime import date
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PatientProfile, Caretaker
from .serializers import PatientProfileSerializer, CaretakerSerializer
from apps.doses.models import DoseLog
from apps.doses.serializers import DoseLogSerializer

class PatientProfileViewSet(viewsets.ModelViewSet):
    """
    Feature #8: Patient Profile CRUD.
    """
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return PatientProfile.objects.all()
        elif user.role == 'caretaker':
            try:
                return user.caretaker_profile.patients.all()
            except Caretaker.DoesNotExist:
                return PatientProfile.objects.none()
        return PatientProfile.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def save_whatsapp(self, request):
        """Feature #9: Save WhatsApp number directly without OTP verification."""
        number = request.data.get('whatsapp_number')
        if not number:
            return Response({'error': 'WhatsApp number required'}, status=400)
        request.user.whatsapp_number = number
        request.user.save()
        return Response({'success': True, 'whatsapp_number': number})

    @action(detail=False, methods=['post'])
    def complete_onboarding(self, request):
        """Feature #13: Mark patient onboarding as done."""
        try:
            profile = request.user.patient_profile
            profile.onboarding_done = True
            profile.save()
            return Response({'onboarding_done': True})
        except PatientProfile.DoesNotExist:
            return Response({'error': 'Patient profile not found'}, status=404)


class CaretakerViewSet(viewsets.ModelViewSet):
    """
    Feature #61: Caretaker Patient Assignment.
    """
    serializer_class = CaretakerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Caretaker.objects.all()
        return Caretaker.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def assign_patient(self, request, pk=None):
        caretaker = self.get_object()
        patient_id = request.data.get('patient_id')
        try:
            patient = PatientProfile.objects.get(id=patient_id)
            caretaker.patients.add(patient)
            return Response({'success': True})
        except PatientProfile.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=404)

    @action(detail=False, methods=['post'])
    def link_patient(self, request):
        """
        Allows a caretaker to link a patient to their profile using the patient's email.
        POST /api/patients/caretakers/link_patient/
        """
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Patient email is required'}, status=400)
            
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            patient_user = User.objects.get(email__iexact=email.strip(), role='patient')
            patient_profile = patient_user.patient_profile
        except User.DoesNotExist:
            return Response({'error': 'No patient found with this email.'}, status=404)
        except PatientProfile.DoesNotExist:
            return Response({'error': 'The user has not completed onboarding yet.'}, status=400)
            
        try:
            caretaker = request.user.caretaker_profile
        except Caretaker.DoesNotExist:
            caretaker = Caretaker.objects.create(user=request.user)
            
        # Add patient to caretaker's patient list
        if caretaker.patients.filter(id=patient_profile.id).exists():
            return Response({'error': 'This patient is already linked to your profile.'}, status=400)
            
        caretaker.patients.add(patient_profile)
        
        # Return serialized profile data
        return Response({
            'success': True,
            'patient': PatientProfileSerializer(patient_profile).data
        })

    @action(detail=False, methods=['post'])
    def create_and_link_patient(self, request):
        """
        Allows a caretaker to create a brand new patient and link them to their profile.
        POST /api/patients/caretakers/create_and_link_patient/
        """
        data = request.data
        name = data.get('name')
        email = data.get('email')
        age = data.get('age')
        gender = data.get('gender')
        blood_group = data.get('blood_group')
        diseases = data.get('diseases', [])
        allergies = data.get('allergies', [])
        chronic_conditions = data.get('chronic_conditions', [])
        whatsapp_number = data.get('whatsapp_number')
        emergency_phone = data.get('emergency_phone')

        if not name or not email or not age or not gender:
            return Response({'error': 'Name, email, age, and gender are required.'}, status=400)

        # Check if email is already taken
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email__iexact=email.strip()).exists():
            return Response({'error': 'A user with this email already exists. Use the "Link Existing Patient" tab.'}, status=400)

        # Create user
        import random
        import string
        dummy_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        user = User.objects.create_user(
            username=email.strip().split('@')[0],
            email=email.strip(),
            password=dummy_password,
            full_name=name,
            role='patient',
            whatsapp_number=whatsapp_number or None
        )

        # Parse conditions
        if isinstance(diseases, str):
            diseases = [d.strip() for d in diseases.split(',') if d.strip()]
        if isinstance(allergies, str):
            allergies = [a.strip() for a in allergies.split(',') if a.strip()]
        if isinstance(chronic_conditions, str):
            chronic_conditions = [c.strip() for c in chronic_conditions.split(',') if c.strip()]

        # Create PatientProfile
        profile = PatientProfile.objects.create(
            user=user,
            age=int(age),
            gender=gender,
            blood_group=blood_group or None,
            diseases=diseases,
            allergies=allergies,
            chronic_conditions=chronic_conditions,
            emergency_phone=emergency_phone or None,
            onboarding_done=True
        )

        # Link to Caretaker
        try:
            caretaker = request.user.caretaker_profile
        except Caretaker.DoesNotExist:
            caretaker = Caretaker.objects.create(user=request.user)

        caretaker.patients.add(profile)

        return Response({
            'success': True,
            'patient': PatientProfileSerializer(profile).data
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def caretaker_dashboard(request):
    """
    Feature #63: aggregate patient data for caretaker view.
    Returns caretaker's assigned patients with today's dose statuses.
    """
    user = request.user
    if user.role != 'caretaker' and user.role != 'admin':
        return Response({'error': 'Access denied: Caretaker or Admin role required'}, status=403)
    
    try:
        if user.role == 'admin':
            patients = PatientProfile.objects.all()
        else:
            patients = user.caretaker_profile.patients.all()
    except Caretaker.DoesNotExist:
        return Response({'error': 'Caretaker profile not found'}, status=404)
        
    result = []
    today = date.today()
    for patient in patients:
        doses = DoseLog.objects.filter(patient=patient, scheduled_date=today).select_related('medicine')
        taken_count = doses.filter(status='taken').count()
        total_count = doses.count()
        
        result.append({
            'patient_id': patient.id,
            'patient_name': patient.user.full_name,
            'age': patient.age,
            'gender': patient.gender,
            'risk_level': patient.risk_level,
            'adherence_score': patient.adherence_score,
            'today_doses': DoseLogSerializer(doses, many=True).data,
            'compliance': {
                'taken': taken_count,
                'total': total_count,
            }
        })
        
    return Response({'patients': result})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def patient_onboarding(request):
    """
    Onboards a patient by creating/updating their PatientProfile and setting onboarding_done=True.
    POST /api/patients/onboarding/
    """
    user = request.user
    if user.role != 'patient':
        return Response({'error': 'Only patients can complete onboarding'}, status=403)
        
    data = request.data
    age = data.get('age')
    gender = data.get('gender')
    blood_group = data.get('blood_group')
    medical_conditions = data.get('medical_conditions', '')
    whatsapp_number = data.get('whatsapp_number')
    emergency_contact = data.get('emergency_contact')
    
    if not age:
        return Response({'error': 'Age is required'}, status=400)
    if not gender:
        return Response({'error': 'Gender is required'}, status=400)
        
    # Update user properties
    if whatsapp_number:
        user.whatsapp_number = whatsapp_number
        user.save()
        
    # Parse conditions
    diseases = [c.strip() for c in str(medical_conditions).split(',') if c.strip()]
    
    # Get or create PatientProfile
    profile, created = PatientProfile.objects.get_or_create(
        user=user,
        defaults={
            'age': int(age),
            'gender': gender,
            'blood_group': blood_group or None,
            'diseases': diseases,
            'emergency_phone': emergency_contact or None,
            'onboarding_done': True
        }
    )
    
    if not created:
        profile.age = int(age)
        profile.gender = gender
        profile.blood_group = blood_group or None
        profile.diseases = diseases
        profile.emergency_phone = emergency_contact or None
        profile.onboarding_done = True
        profile.save()
        
    return Response({
        'success': True,
        'onboarding_done': True,
        'profile': PatientProfileSerializer(profile).data
    })


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def patient_me(request):
    """
    Returns or updates the current authenticated patient's profile.
    GET /api/patients/me/
    PATCH /api/patients/me/
    """
    user = request.user
    try:
        profile = user.patient_profile
    except PatientProfile.DoesNotExist:
        return Response({'error': 'No profile found. Complete onboarding first.'}, status=404)
        
    if request.method == 'GET':
        serializer = PatientProfileSerializer(profile)
        return Response(serializer.data)
        
    elif request.method == 'PATCH':
        data = request.data.copy()
        
        # Sync whatsapp_number back to User model if passed
        whatsapp_number = data.get('whatsapp_number')
        if whatsapp_number:
            user.whatsapp_number = whatsapp_number
            user.save()
            
        # If frontend sends medical_conditions as comma-separated string, convert to diseases JSON field
        medical_conditions = data.get('medical_conditions')
        if medical_conditions is not None:
            data['diseases'] = [c.strip() for c in str(medical_conditions).split(',') if c.strip()]
            
        # If frontend sends emergency_contact, map to emergency_phone
        emergency_contact = data.get('emergency_contact')
        if emergency_contact is not None:
            data['emergency_phone'] = emergency_contact
            
        serializer = PatientProfileSerializer(profile, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
