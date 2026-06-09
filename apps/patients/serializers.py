"""
Serializers for Patient Profile and Caretaker models.
Converts database objects ↔ JSON for the API.
"""
from rest_framework import serializers
from .models import PatientProfile, Caretaker
from apps.users.serializers import UserSerializer


class PatientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for PatientProfile.
    - Shows user info (name, email) as nested read-only data
    - Accepts medical fields (age, gender, diseases, etc.) for create/update
    """

    # 'user' field shows full user info in responses, but is READ ONLY
    # (we set the user automatically in the view, not from user input)
    user = UserSerializer(read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            'id',
            'user',              # Nested: {id, username, full_name, email, role, ...}
            'age',
            'gender',
            'blood_group',
            'diseases',          # JSON array: ["Diabetes", "Hypertension"]
            'allergies',         # JSON array: ["Penicillin"]
            'chronic_conditions',# JSON array: ["Asthma"]
            'emergency_phone',
            'adherence_score',   # Read-only, set by AI engine
            'risk_level',        # Read-only, set by AI engine
            'onboarding_done',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'adherence_score', 'risk_level',
            'created_at', 'updated_at',
        ]


class PatientOnboardingSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for the onboarding wizard.
    Only the fields needed during onboarding.
    """
    # WhatsApp number is on the User model, not PatientProfile
    whatsapp_number = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Patient's WhatsApp number (E.164 format)"
    )

    class Meta:
        model = PatientProfile
        fields = [
            'age',
            'gender',
            'blood_group',
            'diseases',
            'allergies',
            'chronic_conditions',
            'emergency_phone',
            'whatsapp_number',   # This goes to User model
        ]

    def create(self, validated_data):
        """
        Custom create: save WhatsApp number to User, rest to PatientProfile.
        """
        # Pop whatsapp_number — it belongs to User, not PatientProfile
        whatsapp_number = validated_data.pop('whatsapp_number', None)

        # Get the current user from the view's context
        user = self.context['request'].user

        # Save WhatsApp number on the User model
        if whatsapp_number:
            user.whatsapp_number = whatsapp_number
            user.save(update_fields=['whatsapp_number'])

        # Create the PatientProfile
        profile = PatientProfile.objects.create(
            user=user,
            onboarding_done=True,  # Mark onboarding as complete
            **validated_data
        )
        return profile

    def update(self, instance, validated_data):
        """
        Custom update: handle WhatsApp number separately.
        """
        whatsapp_number = validated_data.pop('whatsapp_number', None)
        if whatsapp_number:
            instance.user.whatsapp_number = whatsapp_number
            instance.user.save(update_fields=['whatsapp_number'])

        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CaretakerSerializer(serializers.ModelSerializer):
    """Serializer for Caretaker model."""
    user = UserSerializer(read_only=True)
    patient_count = serializers.SerializerMethodField()

    class Meta:
        model = Caretaker
        fields = [
            'id',
            'user',
            'phone',
            'is_primary',
            'patient_count',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def get_patient_count(self, obj):
        """How many patients this caretaker monitors."""
        return obj.patients.count()