from rest_framework import serializers
from .models import EscalationLog


class EscalationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscalationLog
        fields = '__all__'
        read_only_fields = ['created_at']
