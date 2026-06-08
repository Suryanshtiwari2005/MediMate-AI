from rest_framework import serializers
from .models import Medicine, MedicineSchedule


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'


class MedicineScheduleSerializer(serializers.ModelSerializer):
    medicine = MedicineSerializer(read_only=True)
    medicine_id = serializers.PrimaryKeyRelatedField(
        queryset=Medicine.objects.all(), source='medicine', write_only=True
    )

    class Meta:
        model = MedicineSchedule
        fields = '__all__'
        read_only_fields = ['patient', 'created_at']
