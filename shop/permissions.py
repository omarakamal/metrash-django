from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Allow only staff users (admins)."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)