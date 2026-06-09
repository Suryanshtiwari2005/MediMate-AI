from django.urls import path
from . import views

urlpatterns = [
    # Daily dose tracking
    path('today/', views.today_doses, name='doses-today'),
    path('<int:dose_id>/take/', views.take_dose, name='dose-take'),
    path('<int:dose_id>/skip/', views.skip_dose, name='dose-skip'),

    # History & reports
    path('history/', views.dose_history, name='doses-history'),
    path('weekly/', views.weekly_calendar, name='doses-weekly'),
    path('missed/', views.missed_doses, name='doses-missed'),
    path('summary/', views.adherence_summary, name='doses-summary'),
]