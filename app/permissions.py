# permissions.py
from rest_framework import permissions

# class IsConsultant(permissions.BasePermission):
#     """
#     Allows access only to users with the CONSULTANT role.
#     """
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_authenticated and request.user.role == 'CONSULTANT')
    

# permissions.py
from rest_framework import permissions

class IsConsultant(permissions.BasePermission):
    """
    Allows access only to users with the CONSULTANT role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'CONSULTANT'

class IsClient(permissions.BasePermission):
    """
    Allows access only to users with the CLIENT role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'CLIENT'