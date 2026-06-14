"""
Dose Tracking API — the heart of MediMateAI.

Patients use these endpoints daily to:
- See today's medications
- Mark doses as taken
- Skip doses with a reason
- View history and weekly calendar
"""
from datetime import date, timedelta

from django.utils import timezone
from django.db.models import Count, Q

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import DoseLog
from .serializers import DoseLogSerializer, DoseActionSerializer
from apps.patients.permissions import IsPatient


# ──────────────────────────────────────────────
# 1. TODAY'S DOSES
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPatient])
def today_doses(request):
    """
    Feature #23: Today's Doses View.

    Returns all doses for today with a summary.
    GET /api/doses/today/

    Response:
    {
        "date": "2026-06-09",
        "doses": [...],
        "summary": {"total": 5, "taken": 3, "pending": 1, "missed": 1, "skipped": 0}
    }
    """
    today = date.today()
    from apps.patients.models import PatientProfile
    try:
        patient = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        return Response({
            'date': today.isoformat(),
            'doses': [],
            'summary': {'total': 0, 'taken': 0, 'pending': 0, 'missed': 0, 'skipped': 0, 'rescheduled': 0},
        })

    doses = DoseLog.objects.filter(
        patient=patient,
        scheduled_date=today
    ).select_related('medicine').order_by('scheduled_time')

    # Build summary counts
    summary = {
        'total': doses.count(),
        'taken': doses.filter(status='taken').count(),
        'pending': doses.filter(status='pending').count(),
        'missed': doses.filter(status='missed').count(),
        'skipped': doses.filter(status='skipped').count(),
        'rescheduled': doses.filter(status='rescheduled').count(),
    }

    serializer = DoseLogSerializer(doses, many=True)

    return Response({
        'date': today.isoformat(),
        'doses': serializer.data,
        'summary': summary,
    })


# ──────────────────────────────────────────────
# 2. MARK DOSE AS TAKEN
# ──────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsPatient])
def take_dose(request, dose_id):
    """
    Feature #24: Mark Dose as Taken.
    Feature #26: Duplicate Take Prevention (409 Conflict).

    POST /api/doses/{dose_id}/take/

    Records the current timestamp as taken_at.
    Returns 409 if already taken.
    """
    try:
        dose = DoseLog.objects.get(
            id=dose_id,
            patient=request.user.patient_profile
        )
    except DoseLog.DoesNotExist:
        return Response(
            {"error": "Dose not found or not yours."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Feature #26: Prevent duplicate takes
    if dose.status == 'taken':
        return Response(
            {"error": "This dose is already marked as taken.", "taken_at": dose.taken_at},
            status=status.HTTP_409_CONFLICT
        )

    # Mark as taken
    dose.status = 'taken'
    dose.taken_at = timezone.now()
    dose.save(update_fields=['status', 'taken_at', 'updated_at'])

    serializer = DoseLogSerializer(dose)
    return Response({
        'message': f'{dose.medicine.name} marked as taken ✅',
        'dose': serializer.data,
    })


# ──────────────────────────────────────────────
# 3. SKIP DOSE
# ──────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsPatient])
def skip_dose(request, dose_id):
    """
    Feature #25: Skip Dose with Reason.

    POST /api/doses/{dose_id}/skip/
    Body: { "reason": "Feeling nauseous" }

    Records the skip reason. Triggers escalation if needed.
    """
    try:
        dose = DoseLog.objects.get(
            id=dose_id,
            patient=request.user.patient_profile
        )
    except DoseLog.DoesNotExist:
        return Response(
            {"error": "Dose not found or not yours."},
            status=status.HTTP_404_NOT_FOUND
        )

    if dose.status == 'taken':
        return Response(
            {"error": "Cannot skip a dose that's already taken."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate the reason
    action_serializer = DoseActionSerializer(data=request.data)
    action_serializer.is_valid(raise_exception=True)

    # Mark as skipped
    dose.status = 'skipped'
    dose.skip_reason = action_serializer.validated_data.get('reason', 'No reason provided')
    dose.save(update_fields=['status', 'skip_reason', 'updated_at'])

    serializer = DoseLogSerializer(dose)
    return Response({
        'message': f'{dose.medicine.name} skipped',
        'dose': serializer.data,
    })


# ──────────────────────────────────────────────
# 4. DOSE HISTORY
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPatient])
def dose_history(request):
    """
    Feature #27: Dose History with Filters.

    GET /api/doses/history/?start_date=2026-06-01&end_date=2026-06-07&status=missed

    Query params (all optional):
    - start_date: YYYY-MM-DD (default: 7 days ago)
    - end_date: YYYY-MM-DD (default: today)
    - status: pending/taken/missed/skipped (filter by status)
    """
    from apps.patients.models import PatientProfile
    try:
        patient = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        end_date_val = date.today()
        start_date_val = end_date_val - timedelta(days=7)
        if start_date_str:
            try:
                start_date_val = date.fromisoformat(start_date_str)
            except ValueError:
                return Response({"error": "Invalid start_date format. Use YYYY-MM-DD."}, status=400)
        if end_date_str:
            try:
                end_date_val = date.fromisoformat(end_date_str)
            except ValueError:
                return Response({"error": "Invalid end_date format. Use YYYY-MM-DD."}, status=400)
        return Response({
            'start_date': start_date_val.isoformat(),
            'end_date': end_date_val.isoformat(),
            'count': 0,
            'doses': [],
        })

    # Parse date range from query params
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')
    status_filter = request.query_params.get('status')

    # Defaults: last 7 days
    end_date_val = date.today()
    start_date_val = end_date_val - timedelta(days=7)

    if start_date_str:
        try:
            start_date_val = date.fromisoformat(start_date_str)
        except ValueError:
            return Response(
                {"error": "Invalid start_date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

    if end_date_str:
        try:
            end_date_val = date.fromisoformat(end_date_str)
        except ValueError:
            return Response(
                {"error": "Invalid end_date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Query
    doses = DoseLog.objects.filter(
        patient=patient,
        scheduled_date__gte=start_date_val,
        scheduled_date__lte=end_date_val,
    ).select_related('medicine').order_by('-scheduled_date', 'scheduled_time')

    # Optional status filter
    if status_filter:
        doses = doses.filter(status=status_filter)

    serializer = DoseLogSerializer(doses, many=True)
    return Response({
        'start_date': start_date_val.isoformat(),
        'end_date': end_date_val.isoformat(),
        'count': doses.count(),
        'doses': serializer.data,
    })


# ──────────────────────────────────────────────
# 5. WEEKLY CALENDAR
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPatient])
def weekly_calendar(request):
    """
    Feature #28: Weekly Calendar Grid.

    GET /api/doses/weekly/

    Returns a 7-day overview (Mon-Sun of current week) with
    taken/missed/pending counts per day.

    Response:
    {
        "week": [
            {"date": "2026-06-03", "day": "Mon", "taken": 3, "missed": 1, "pending": 0, "total": 4},
            {"date": "2026-06-04", "day": "Tue", ...},
            ...
        ]
    }
    """
    from apps.patients.models import PatientProfile
    try:
        patient = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        week_data = []
        for i in range(7):
            day = monday + timedelta(days=i)
            week_data.append({
                'date': day.isoformat(),
                'day': day.strftime('%a'),
                'is_today': day == today,
                'taken': 0,
                'missed': 0,
                'skipped': 0,
                'pending': 0,
                'total': 0,
            })
        return Response({'week': week_data})
    today = date.today()

    # Get Monday of this week
    monday = today - timedelta(days=today.weekday())

    week_data = []
    for i in range(7):
        day = monday + timedelta(days=i)
        day_doses = DoseLog.objects.filter(
            patient=patient,
            scheduled_date=day,
        )

        week_data.append({
            'date': day.isoformat(),
            'day': day.strftime('%a'),         # Mon, Tue, Wed...
            'is_today': day == today,
            'taken': day_doses.filter(status='taken').count(),
            'missed': day_doses.filter(status='missed').count(),
            'skipped': day_doses.filter(status='skipped').count(),
            'pending': day_doses.filter(status='pending').count(),
            'total': day_doses.count(),
        })

    return Response({'week': week_data})


# ──────────────────────────────────────────────
# 6. MISSED DOSES
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPatient])
def missed_doses(request):
    """
    Feature #29: Missed Doses Report.

    GET /api/doses/missed/?days=7

    Returns all missed doses in the last N days (default: 7).
    """
    from apps.patients.models import PatientProfile
    try:
        patient = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        days = int(request.query_params.get('days', 7))
        since = date.today() - timedelta(days=days)
        return Response({
            'period_days': days,
            'since': since.isoformat(),
            'count': 0,
            'doses': [],
        })

    days = int(request.query_params.get('days', 7))
    since = date.today() - timedelta(days=days)

    doses = DoseLog.objects.filter(
        patient=patient,
        status='missed',
        scheduled_date__gte=since,
    ).select_related('medicine').order_by('-scheduled_date', 'scheduled_time')

    serializer = DoseLogSerializer(doses, many=True)
    return Response({
        'period_days': days,
        'since': since.isoformat(),
        'count': doses.count(),
        'doses': serializer.data,
    })


# ──────────────────────────────────────────────
# 7. ADHERENCE SUMMARY
# ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPatient])
def adherence_summary(request):
    """
    Adherence stats for the patient.

    GET /api/doses/summary/?days=30

    Returns overall adherence percentage and breakdown.
    """
    from apps.patients.models import PatientProfile
    days = int(request.query_params.get('days', 30))
    try:
        patient = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        return Response({
            'period_days': days,
            'adherence_percentage': 100.0,
            'total_doses': 0,
            'taken': 0,
            'missed': 0,
            'skipped': 0,
            'pending': 0,
        })

    since = date.today() - timedelta(days=days)

    doses = DoseLog.objects.filter(
        patient=patient,
        scheduled_date__gte=since,
        scheduled_date__lte=date.today(),
    )

    total = doses.count()
    if total == 0:
        return Response({
            'period_days': days,
            'adherence_percentage': 100.0,
            'total_doses': 0,
            'taken': 0,
            'missed': 0,
            'skipped': 0,
            'pending': 0,
        })

    taken = doses.filter(status='taken').count()
    missed = doses.filter(status='missed').count()
    skipped = doses.filter(status='skipped').count()
    pending = doses.filter(status='pending').count()

    # Adherence = taken / (total - pending) * 100
    completed = total - pending
    adherence = (taken / completed * 100) if completed > 0 else 100.0

    return Response({
        'period_days': days,
        'adherence_percentage': round(adherence, 1),
        'total_doses': total,
        'taken': taken,
        'missed': missed,
        'skipped': skipped,
        'pending': pending,
    })