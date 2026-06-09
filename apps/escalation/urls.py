from django.urls import path
from . import views

urlpatterns = [
    path('logs/', views.list_escalation_logs, name='escalation-logs-list'),
]
