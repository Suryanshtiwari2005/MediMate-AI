from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientProfileViewSet,
    CaretakerViewSet,
    caretaker_dashboard,
    patient_onboarding,
    patient_me,
    assign_caretaker,
    remove_caretaker,
)

router = DefaultRouter()
router.register(r'profiles', PatientProfileViewSet, basename='patient-profile')
router.register(r'caretakers', CaretakerViewSet, basename='caretaker')

# Direct mappings to support frontend endpoints
patient_list = PatientProfileViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

patient_detail = PatientProfileViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('onboarding/', patient_onboarding, name='patient-onboarding'),
    path('me/', patient_me, name='patient-me'),
    path('caretaker-dashboard/', caretaker_dashboard, name='caretaker-dashboard'),
    path('assign-caretaker/', assign_caretaker, name='assign-caretaker'),
    path('remove-caretaker/', remove_caretaker, name='remove-caretaker'),
    path('', patient_list, name='patient-list'),
    path('<int:pk>/', patient_detail, name='patient-detail'),
    path('', include(router.urls)),
]
