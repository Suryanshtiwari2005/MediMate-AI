from django.contrib import admin
from .models import WhatsAppInteraction


@admin.register(WhatsAppInteraction)
class WhatsAppInteractionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'whatsapp_number', 'status', 'response_received', 'sent_at']
    list_filter = ['status', 'response_received']
    search_fields = ['whatsapp_number', 'patient__user__full_name']
