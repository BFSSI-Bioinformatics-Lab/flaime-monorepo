from rest_framework import permissions


class IsAdminGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Admin').exists()


class IsStaffGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Staff').exists() or request.user.groups.filter(name='Admin').exists()


class IsBasicGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
