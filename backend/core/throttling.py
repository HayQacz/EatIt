from rest_framework.throttling import UserRateThrottle


class RoleBasedThrottle(UserRateThrottle):
    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            self.scope = 'anon'
        else:
            role = request.user.role
            if role == 'manager':
                self.scope = 'manager'
            elif role == 'waiter':
                self.scope = 'waiter'
            elif role == 'kitchen':
                self.scope = 'kitchen'
            else:
                self.scope = 'client'
        return super().get_cache_key(request, view)
