from rest_framework import permissions


class AuthorAdminPermission(permissions.BasePermission):
    """Только автор и админ могут добавлять и изменять объекты."""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS or (
            request.user == obj.author) or request.user.is_staff)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_staff)
