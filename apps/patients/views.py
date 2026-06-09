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
