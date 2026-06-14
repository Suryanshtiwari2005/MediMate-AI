from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'is_ai_nudge', 'is_reminder', 'is_read', 'created_at']
    list_filter = ['is_ai_nudge', 'is_reminder', 'is_read']
    search_fields = ['sender__full_name', 'recipient__full_name', 'message']
