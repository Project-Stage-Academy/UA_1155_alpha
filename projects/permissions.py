from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class InvestorPermissionDenied(PermissionDenied):
    default_detail = "Access denied. The first step is to sign up as an investor."
    default_code = 'not_investor'


class IsInvestor(permissions.BasePermission):
    """
    Custom permission to only allow access to users who are investors.

    This permission class checks if the user is authenticated and if the user
    has the 'is_investor' attribute set to True. If the user is not authenticated,
    access is denied. If the user is authenticated but is not an investor,
    a custom permission denied exception is raised with a detailed message.

    Methods
    -------
    has_permission(request, view)
        Checks if the user is authenticated and an investor.
        Raises a custom permission denied exception if the user is not an investor.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if not request.user.is_investor:
            raise InvestorPermissionDenied()
        return True
