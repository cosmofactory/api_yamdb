from rest_framework import permissions


class ReviewCommentPermission(permissions.BasePermission):
    """
    Checking permissions to create and edit records for:
    - user;
    - moderator;
    - admin.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )