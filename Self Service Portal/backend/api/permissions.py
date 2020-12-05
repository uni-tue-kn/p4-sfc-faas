from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it,
    otherwise, read-access is granted.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed to the owner of the snippet.
        return str(obj.owner) == str(request.user)


class IsAdminOrIsSelf(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it,
    otherwise, read-access is granted.
    """
    def has_permission(self, request, view, obj):
        if request.user.is_staff:
            print('IsAdmin')
            return True
        elif request.user.is_authenticated and (str(obj.owner) == str(request.user)):
            print('IsSelf')
            return True
        else:
            return False
