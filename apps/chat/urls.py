from django.urls import path
from . import views

urlpatterns = [
    path('messages/', views.get_messages, name='chat-messages'),
    path('send/', views.send_message, name='chat-send'),
    path('unread-count/', views.get_unread_count, name='chat-unread-count'),
    path('check-conflict/', views.check_medicine_conflict_view, name='chat-check-conflict'),
]
