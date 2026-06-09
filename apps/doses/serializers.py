"""
Serializers for Dose Tracking.
Converts DoseLog objects to/from JSON.
"""
from rest_framework import serializers
from .models import DoseLog


class DoseLogSerializer(serializers.ModelSerializer):
    """
    Full serializer for DoseLog — used in list/detail views.
    Includes medicine name and patient name for readability.
    """
    # These add human-readable fields to the JSON output
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    medicine_dosage = serializers.CharField(source='medicine.dosage', read_only=True)
    medicine_instructions = serializers.CharField(
        source='medicine.instructions', read_only=True, default=''
    )
    patient_name = serializers.CharField(
        source='patient.user.full_name', read_only=True
    )

    class Meta:
        model = DoseLog
        fields = [
            'id',
            'schedule',
            'patient',
            'medicine',
            'medicine_name',        # "Metformin"
            'medicine_dosage',      # "500mg"
            'medicine_instructions',# "After food"
            'patient_name',         # "Rahul Sharma"
            'scheduled_date',
            'scheduled_time',
            'status',               # pending/taken/missed/skipped/rescheduled
            'taken_at',
            'missed_at',
            'skip_reason',
            'reminder_sent',
            'escalated',
            'call_attempted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'schedule', 'patient', 'medicine',
            'medicine_name', 'medicine_dosage', 'medicine_instructions',
            'patient_name', 'scheduled_date', 'scheduled_time',
            'created_at', 'updated_at',
        ]


class DoseActionSerializer(serializers.Serializer):
    """
    For take/skip actions — just needs the reason (for skip).
    Not tied to a model, just validates input.
    """
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Reason for skipping (required for skip action)"
    )