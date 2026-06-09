from rest_framework import serializers
from .models import PatientProfile, Caretaker
from apps.users.serializers import UserSerializer

class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = PatientProfile
        fields = '__all__'
        read_only_fields = ['adherence_score', 'risk_level', 'created_at', 'updated_at']

class CaretakerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Caretaker
        fields = '__all__'
