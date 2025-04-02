from rest_framework.permissions import BasePermission, SAFE_METHODS

class CanViewOrder(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.role in ['manager', 'kitchen', 'waiter']:
            return True

        return obj.user == user


class CanModifyOrderStatus(BasePermission):
    def has_permission(self, request, view):
        return request.method in ['PATCH', 'PUT'] and request.user.role == 'manager'

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'
class IsKitchen(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'kitchen'

class IsWaiter(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'waiter'
