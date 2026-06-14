from rest_framework import serializers
from .models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = '__all__'
        read_only_fields = ['sender', 'created_at']

    def get_sender_name(self, obj):
        return obj.sender.full_name if obj.sender else "MediMate AI"

    def get_recipient_name(self, obj):
        return obj.recipient.full_name if obj.recipient else ""
