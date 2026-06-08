from django.urls import path
from . import views

urlpatterns = [
    path('send-reminder/', views.send_reminder_manual, name='whatsapp-send-reminder'),
    path('interactions/', views.list_interactions, name='whatsapp-interactions'),
    path('webhook/', views.whatsapp_webhook, name='whatsapp-webhook'),
]
