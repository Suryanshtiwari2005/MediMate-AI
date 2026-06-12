from django.contrib import admin
from .models import PatientProfile, Caretaker
from apps.whatsapp.models import WhatsAppInteraction
from apps.escalation.models import EscalationLog

# Inline to show WhatsApp messages sent to this patient
class WhatsAppInteractionInline(admin.TabularInline):
    model = WhatsAppInteraction
    extra = 0
    readonly_fields = ['message_sent', 'response_received', 'status', 'sent_at']
    can_delete = False

# Inline to show Caretaker Escalations for this patient
class EscalationLogInline(admin.TabularInline):
    model = EscalationLog
    extra = 0
    readonly_fields = ['escalation_level', 'recipient_phone', 'message_sent', 'success', 'created_at']
    can_delete = False

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'gender', 'blood_group', 'risk_level', 'adherence_score', 'onboarding_done']
    list_filter = ['gender', 'risk_level', 'onboarding_done']
    search_fields = ['user__full_name', 'user__email']
    inlines = [WhatsAppInteractionInline, EscalationLogInline]


@admin.register(Caretaker)
class CaretakerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'is_primary', 'created_at']
    list_filter = ['is_primary']
    search_fields = ['user__full_name', 'user__email']
