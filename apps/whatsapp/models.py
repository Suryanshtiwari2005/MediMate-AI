from django.db import models


class WhatsAppInteraction(models.Model):
    """Logs every WhatsApp message sent and the patient's response."""
    RESPONSE_CHOICES = (('1', 'Taken'), ('2', 'Reschedule'), ('3', 'Not Taken'))
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('responded', 'Responded'),
        ('expired', 'Expired'),
        ('failed', 'Failed'),
    )
    dose_log = models.ForeignKey('doses.DoseLog', on_delete=models.CASCADE)
    patient = models.ForeignKey('patients.PatientProfile', on_delete=models.CASCADE)
    whatsapp_number = models.CharField(max_length=15)
    message_sent = models.TextField()
    ai_variables = models.JSONField(default=dict, blank=True)
    response_received = models.CharField(max_length=1, choices=RESPONSE_CHOICES, null=True, blank=True)
    response_time = models.DateTimeField(null=True, blank=True)
    rescheduled_to = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"WhatsApp to {self.whatsapp_number} at {self.sent_at} — {self.status}"
