"""
API views for Patient Profile and Caretaker management.

Endpoints:
  POST   /api/patients/onboarding/     → Complete onboarding (create profile)
  GET    /api/patients/me/             → Get my profile
  PUT    /api/patients/me/             → Update my profile
  GET    /api/patients/                → List patients (admin/caretaker only)
  GET    /api/patients/{id}/           → Get specific patient (admin/caretaker)
  POST   /api/patients/assign-caretaker/  → Assign caretaker to patient
  DELETE /api/patients/remove-caretaker/  → Remove caretaker from patient
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import PatientProfile, Caretaker
from .serializers import (
    PatientProfileSerializer,
    PatientOnboardingSerializer,
    CaretakerSerializer,
)
from .permissions import IsPatient, IsCaretakerOrAdmin


# ──────────────────────────────────────────────
# PATIENT OWN PROFILE
# ──────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def onboarding(request):
    """
    Feature #7: Multi-step onboarding — saves patient profile.
    Feature #9: Direct WhatsApp number save.
    Feature #13: Sets onboarding_done = True.

    Called once after Google login when user fills the onboarding wizard.
    """
    user = request.user

    # Check if profile already exists
    if hasattr(user, 'patient_profile'):
        return Response(
            {"error": "Profile already exists. Use PUT /api/patients/me/ to update."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Make sure user is a patient
    if user.role != 'patient':
        return Response(
            {"error": "Only patients can complete onboarding."},
            status=status.HTTP_403_FORBIDDEN
        )

    data = request.data.copy() if hasattr(request.data, 'copy') else request.data
    gender = data.get('gender')
    if gender and isinstance(gender, str):
        data['gender'] = gender.lower()

    serializer = PatientOnboardingSerializer(
        data=data,
        context={'request': request}  # Pass request so serializer can access user
    )
    if serializer.is_valid():
        profile = serializer.save()
        # Return full profile with user info
        return Response(
            PatientProfileSerializer(profile).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsPatient])
def my_profile(request):
    """
    Feature #8: Patient Profile CRUD — get or update own profile.

    GET  → Returns the patient's own profile (or a dummy in-memory one if not onboarded)
    PUT  → Full update of profile (or create and update if not onboarded)
    PATCH → Partial update of profile (or create and update if not onboarded)
    """
    try:
        profile = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        if request.method == 'GET':
            profile = PatientProfile(
                id=request.user.id,
                user=request.user,
                age=0,
                gender='other',
                blood_group='',
                diseases=[],
                allergies=[],
                chronic_conditions=[],
                emergency_phone='',
                onboarding_done=False
            )
            serializer = PatientProfileSerializer(profile)
            return Response(serializer.data)
        elif request.method in ('PUT', 'PATCH'):
            profile = PatientProfile.objects.create(
                user=request.user,
                age=0,
                gender='other',
                onboarding_done=True
            )
        else:
            return Response(
                {"error": "No profile found. Complete onboarding first."},
                status=status.HTTP_404_NOT_FOUND
            )

    if request.method == 'GET':
        serializer = PatientProfileSerializer(profile)
        return Response(serializer.data)

    # PUT or PATCH
    data = request.data.copy() if hasattr(request.data, 'copy') else request.data
    gender = data.get('gender')
    if gender and isinstance(gender, str):
        data['gender'] = gender.lower()

    serializer = PatientOnboardingSerializer(
        profile,
        data=data,
        partial=(request.method == 'PATCH'),  # PATCH = only send changed fields
        context={'request': request}
    )
    if serializer.is_valid():
        profile = serializer.save()
        return Response(PatientProfileSerializer(profile).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────
# PATIENT LIST (for caretakers & admins)
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCaretakerOrAdmin])
def list_patients(request):
    """
    List patients — filtered by role:
    - Caretaker: sees only their assigned patients
    - Admin: sees all patients
    """
    if request.user.role == 'admin':
        patients = PatientProfile.objects.select_related('user').all()
    else:
        # Caretaker — only assigned patients
        try:
            caretaker = request.user.caretaker_profile
            patients = caretaker.patients.select_related('user').all()
        except Caretaker.DoesNotExist:
            return Response(
                {"error": "Caretaker profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    serializer = PatientProfileSerializer(patients, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCaretakerOrAdmin])
def get_patient(request, patient_id):
    """Get a specific patient's profile (caretaker/admin only)."""
    from django.db.models import Q
    from apps.users.models import User
    try:
        patient = PatientProfile.objects.select_related('user').filter(
            Q(id=patient_id) | Q(user_id=patient_id)
        ).first()
        if not patient:
            # Fallback: check if User exists with this ID who has role='patient'
            user_obj = User.objects.filter(id=patient_id, role='patient').first()
            if user_obj:
                patient = PatientProfile(
                    id=user_obj.id,
                    user=user_obj,
                    age=0,
                    gender='other',
                    blood_group='',
                    diseases=[],
                    allergies=[],
                    chronic_conditions=[],
                    emergency_phone='',
                    onboarding_done=False
                )
            else:
                raise PatientProfile.DoesNotExist()
    except PatientProfile.DoesNotExist:
        return Response(
            {"error": "Patient not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Caretakers can only see their assigned patients
    if request.user.role == 'caretaker':
        try:
            caretaker = request.user.caretaker_profile
            if not caretaker.patients.filter(Q(id=patient_id) | Q(user_id=patient_id)).exists():
                return Response(
                    {"error": "You are not assigned to this patient."},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Caretaker.DoesNotExist:
            return Response(
                {"error": "Caretaker profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    serializer = PatientProfileSerializer(patient)
    return Response(serializer.data)


# ──────────────────────────────────────────────
# CARETAKER ASSIGNMENT
# ──────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_caretaker(request):
    """
    Feature #61: Assign a caretaker to a patient.

    Body: { "patient_id": 1, "caretaker_id": 2 }
    Only admins or the caretaker themselves can do this.
    """
    patient_id = request.data.get('patient_id')
    caretaker_id = request.data.get('caretaker_id')

    if not patient_id or not caretaker_id:
        return Response(
            {"error": "Both patient_id and caretaker_id are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        patient = PatientProfile.objects.get(id=patient_id)
        caretaker = Caretaker.objects.get(id=caretaker_id)
    except PatientProfile.DoesNotExist:
        return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)
    except Caretaker.DoesNotExist:
        return Response({"error": "Caretaker not found."}, status=status.HTTP_404_NOT_FOUND)

    # Add patient to caretaker's list (M2M)
    caretaker.patients.add(patient)

    return Response({
        "message": f"Caretaker {caretaker.user.full_name} assigned to patient {patient.user.full_name}",
        "caretaker": CaretakerSerializer(caretaker).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_caretaker(request):
    """Remove a caretaker from a patient."""
    patient_id = request.data.get('patient_id')
    caretaker_id = request.data.get('caretaker_id')

    if not patient_id or not caretaker_id:
        return Response(
            {"error": "Both patient_id and caretaker_id are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        patient = PatientProfile.objects.get(id=patient_id)
        caretaker = Caretaker.objects.get(id=caretaker_id)
    except (PatientProfile.DoesNotExist, Caretaker.DoesNotExist):
        return Response({"error": "Patient or Caretaker not found."}, status=status.HTTP_404_NOT_FOUND)

    caretaker.patients.remove(patient)

    return Response({
        "message": f"Caretaker {caretaker.user.full_name} removed from patient {patient.user.full_name}",
    })