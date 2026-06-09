"""
Role-based permissions for MediMateAI.
Controls who can access patient and caretaker data.
"""
from rest_framework.permissions import BasePermission


class IsPatient(BasePermission):
    """
    Only users with role='patient' can access this view.
    Used for: patient profile, dose tracking, etc.
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'patient'
        )


class IsCaretaker(BasePermission):
    """
    Only users with role='caretaker' can access this view.
    Used for: caretaker dashboard, patient monitoring.
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'caretaker'
        )


class IsAdmin(BasePermission):
    """
    Only users with role='admin' can access this view.
    Used for: admin dashboard, system stats.
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsPatientOrAdmin(BasePermission):
    """Patient or Admin can access."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ('patient', 'admin')
        )


class IsCaretakerOrAdmin(BasePermission):
    """Caretaker or Admin can access."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ('caretaker', 'admin')
        )