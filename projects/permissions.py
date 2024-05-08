from rest_framework import permissions


class IsInvestor(permissions.BasePermission):
    """
    Custom permission to only allow access to users who are investors.
    """
    def has_permission(self, request, view):
        # Проверить, что пользователь аутентифицирован
        if not request.user.is_authenticated:
            return False
        # Проверить, что пользователь является инвестором
        return request.user.is_investor
