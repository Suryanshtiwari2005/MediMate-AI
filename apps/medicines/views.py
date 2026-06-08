from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Medicine, MedicineSchedule
from .serializers import MedicineSerializer, MedicineScheduleSerializer


class MedicineViewSet(viewsets.ModelViewSet):
    """Feature #16: Medicine CRUD — Add, edit, delete medicines."""
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated]


class MedicineScheduleViewSet(viewsets.ModelViewSet):
    """
    Feature #17: Medicine Schedule CRUD — Set daily times with start/end dates.
    Feature #21: Schedule Activation Toggle — is_active flag to pause/resume.
    """
    serializer_class = MedicineScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return MedicineSchedule.objects.all()
        return MedicineSchedule.objects.filter(patient__user=user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user.patient_profile)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Feature #21: Toggle is_active flag without deleting the schedule."""
        schedule = self.get_object()
        schedule.is_active = not schedule.is_active
        schedule.save()
        return Response({
            'id': schedule.id,
            'is_active': schedule.is_active,
            'message': f"Schedule {'activated' if schedule.is_active else 'paused'}",
        })
