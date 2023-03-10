from rest_framework.permissions import BasePermission



class IsOwner(BasePermission):

    def has_permission(self, request, view):
        return request.user.role.lower() == "owner" and request.user.is_created
