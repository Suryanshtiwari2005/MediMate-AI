from django.db import models


class ChatMessage(models.Model):
    """In-app chat message between users, including AI nudges and medication reminders."""
    sender = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='sent_chat_messages',
        null=True,
        blank=True,
    )
    recipient = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='received_chat_messages',
    )
    message = models.TextField()
    is_ai_nudge = models.BooleanField(default=False)
    is_reminder = models.BooleanField(default=False)
    dose_log = models.ForeignKey(
        'doses.DoseLog',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        sender_name = self.sender.full_name if self.sender else "System/AI"
        return f"{sender_name} → {self.recipient.full_name}: {self.message[:50]}"
