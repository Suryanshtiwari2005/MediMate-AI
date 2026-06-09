import logging
from datetime import date, timedelta
from django.db.models import Count, Q
from apps.doses.models import DoseLog

logger = logging.getLogger(__name__)

def calculate_risk_score(patient_id: int) -> dict:
    """
    Feature #45, #46, #47, #48: Deterministic risk engine using 5 factors.
    Returns:
        dict: Containing risk score, level, insight, and detailed breakdown.
    """
    today = date.today()
    week_ago = today - timedelta(days=7)
    base_score = 0.0

    # Factor 1: Recent miss rate (last 7 days) — up to 50 points
    recent = DoseLog.objects.filter(
        patient_id=patient_id,
        scheduled_date__gte=week_ago,
        scheduled_date__lte=today,
    )
    total_7d = recent.count()
    missed_7d = recent.filter(status__in=['missed', 'skipped']).count()
    miss_rate = missed_7d / total_7d if total_7d > 0 else 0.0
    base_score += miss_rate * 50

    # Factor 2: Consecutive missed slots — up to 20 points
    recent_ordered = recent.order_by('-scheduled_date', '-scheduled_time')
    streak = 0
    for dose in recent_ordered:
        if dose.status in ('missed', 'skipped'):
            streak += 1
        else:
            break
    if streak >= 3:
        base_score += 20

    # Factor 3: Medicine complexity — up to 10 points
    from apps.medicines.models import MedicineSchedule
    active_schedules = MedicineSchedule.objects.filter(
        patient_id=patient_id, is_active=True
    ).count()
    if active_schedules >= 4:
        base_score += 10

    # Factor 4: Day-of-week pattern — up to 10 points
    day_misses = DoseLog.objects.filter(
        patient_id=patient_id, status='missed'
    ).values('scheduled_date__week_day').annotate(
        count=Count('id')
    ).order_by('-count').first()
    if day_misses:
        # Django week_day: 1=Sunday, 2=Monday, etc.
        today_weekday = today.isoweekday() % 7 + 1
        if day_misses['scheduled_date__week_day'] == today_weekday:
            base_score += 10

    # Factor 5: Consecutive missed DAYS — up to 10 points
    consec_days = 0
    check = today - timedelta(days=1)
    for _ in range(7):
        day_doses = DoseLog.objects.filter(patient_id=patient_id, scheduled_date=check)
        if day_doses.exists() and not day_doses.filter(status='taken').exists():
            consec_days += 1
            check -= timedelta(days=1)
        else:
            break
    if consec_days >= 2:
        base_score += 10

    risk_score = min(round(base_score), 100)
    thresholds = [(25, 'low'), (50, 'medium'), (75, 'high'), (101, 'critical')]
    level = next((lbl for t, lbl in thresholds if risk_score < t), 'critical')

    insights = {
        'low': "You're doing great! Keep up the consistency. 💚",
        'medium': "Some doses were missed recently. Let's get back on track! 💛",
        'high': "Multiple missed doses detected. Your health needs attention! 🧡",
        'critical': "Urgent: High risk of medication non-adherence. Please take action! ❤️",
    }

    return {
        'score': risk_score,
        'level': level,
        'insight': insights[level],
        'factors': {
            'miss_rate_7d': round(miss_rate * 100, 1),
            'slot_streak': streak,
            'active_medicines': active_schedules,
            'consecutive_missed_days': consec_days,
        },
    }


def get_7d_predictions(patient_id: int) -> list:
    """
    Feature #49: Predicts upcoming doses in the next 7 days that are at risk.
    """
    from apps.medicines.models import MedicineSchedule
    from datetime import date, timedelta
    
    today = date.today()
    end_date = today + timedelta(days=7)
    
    schedules = MedicineSchedule.objects.filter(patient_id=patient_id, is_active=True).select_related('medicine')
    
    predictions = []
    
    # Calculate historical miss rates by medicine
    recent_doses = DoseLog.objects.filter(patient_id=patient_id, scheduled_date__gte=today - timedelta(days=30))
    total_by_med = {}
    missed_by_med = {}
    
    for d in recent_doses:
        med_id = d.medicine_id
        total_by_med[med_id] = total_by_med.get(med_id, 0) + 1
        if d.status in ('missed', 'skipped'):
            missed_by_med[med_id] = missed_by_med.get(med_id, 0) + 1
            
    risk_info = calculate_risk_score(patient_id)
    base_risk = risk_info['score']
    
    current = today
    while current <= end_date:
        for schedule in schedules:
            if schedule.start_date <= current and (not schedule.end_date or current <= schedule.end_date):
                med_id = schedule.medicine_id
                med_miss_rate = missed_by_med.get(med_id, 0) / total_by_med.get(med_id, 1) if total_by_med.get(med_id, 0) > 0 else 0.0
                
                # Combine base patient risk and specific medicine miss rate
                prob = (0.4 * (base_risk / 100.0)) + (0.6 * med_miss_rate)
                
                if total_by_med.get(med_id, 0) == 0:
                    prob = base_risk / 100.0
                    
                risk_pct = min(round(prob * 100), 100)
                
                if risk_pct < 25:
                    dose_risk = 'low'
                elif risk_pct < 50:
                    dose_risk = 'medium'
                elif risk_pct < 75:
                    dose_risk = 'high'
                else:
                    dose_risk = 'critical'
                    
                predictions.append({
                    'date': current.isoformat(),
                    'day_name': current.strftime('%A'),
                    'medicine_name': schedule.medicine.name,
                    'dosage': schedule.medicine.dosage,
                    'scheduled_time': schedule.scheduled_time.strftime("%I:%M %p"),
                    'risk_percentage': risk_pct,
                    'risk_level': dose_risk,
                })
        current += timedelta(days=1)
        
    risk_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    predictions.sort(key=lambda x: (risk_order[x['risk_level']], x['date']))
    
    return predictions


def get_adherence_trend(patient_id: int) -> list:
    """
    Feature #50: Calculate weekly compliance rates for the last 4 weeks.
    """
    from datetime import date, timedelta
    
    today = date.today()
    trend = []
    
    for w in range(4):
        start_date = today - timedelta(days=(4-w)*7)
        end_date = start_date + timedelta(days=6)
        
        doses = DoseLog.objects.filter(
            patient_id=patient_id,
            scheduled_date__gte=start_date,
            scheduled_date__lte=end_date
        )
        total = doses.count()
        taken = doses.filter(status='taken').count()
        rate = round((taken / total * 100), 1) if total > 0 else 100.0
        
        trend.append({
            'week_label': f"Wk {w+1} ({start_date.strftime('%b %d')})",
            'compliance_rate': rate,
            'taken': taken,
            'total': total,
        })
        
    return trend
