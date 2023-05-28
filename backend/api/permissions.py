from rest_framework import permissions


class AuthorPermission(permissions.BasePermission):
    """Только автор может добавлять и изменять объекты."""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
