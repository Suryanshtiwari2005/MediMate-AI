from django.urls import path
from . import views

urlpatterns = [
    # Patient's own profile
    path('onboarding/', views.onboarding, name='patient-onboarding'),
    path('me/', views.my_profile, name='patient-my-profile'),

    # Patient list (caretaker/admin)
    path('', views.list_patients, name='patient-list'),
    path('<int:patient_id>/', views.get_patient, name='patient-detail'),

    # Caretaker assignment
    path('assign-caretaker/', views.assign_caretaker, name='assign-caretaker'),
    path('remove-caretaker/', views.remove_caretaker, name='remove-caretaker'),
]