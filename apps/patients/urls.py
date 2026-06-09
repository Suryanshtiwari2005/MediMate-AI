from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientProfileViewSet, CaretakerViewSet, caretaker_dashboard

router = DefaultRouter()
router.register(r'profiles', PatientProfileViewSet, basename='patient-profile')
router.register(r'caretakers', CaretakerViewSet, basename='caretaker')

urlpatterns = [
    path('caretaker-dashboard/', caretaker_dashboard, name='caretaker-dashboard'),
    path('', include(router.urls)),
]
