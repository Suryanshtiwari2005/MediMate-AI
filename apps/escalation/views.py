from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import EscalationLog
from .serializers import EscalationLogSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_escalation_logs(request):
    """List escalation logs — filtered by role."""
    user = request.user
    if user.role == 'admin':
        logs = EscalationLog.objects.all()
    elif user.role == 'caretaker':
        # Show escalations for caretaker's assigned patients
        logs = EscalationLog.objects.filter(
            patient__caretakers__user=user
        )
    else:
        # Show only own escalations
        logs = EscalationLog.objects.filter(patient__user=user)

    logs = logs.order_by('-created_at')

    # Optional date filter
    date_filter = request.GET.get('date')
    if date_filter:
        logs = logs.filter(created_at__date=date_filter)

    return Response({
        'logs': EscalationLogSerializer(logs, many=True).data,
        'count': logs.count(),
    })
