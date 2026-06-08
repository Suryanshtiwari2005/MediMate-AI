from rest_framework import serializers
from .models import WhatsAppInteraction


class WhatsAppInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppInteraction
        fields = '__all__'
        read_only_fields = ['sent_at']
