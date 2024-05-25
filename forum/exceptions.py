from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import exception_handler

from projects.permissions import InvestorPermissionDenied


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data['status_code'] = response.status_code
    if isinstance(exc, InvestorPermissionDenied):
        response = Response({
            'detail': exc.detail,
            'code': exc.default_code
        }, status=status.HTTP_403_FORBIDDEN)
    if isinstance(exc, serializers.ValidationError) and "message" in response.data:
        response.data["message"] = exc.detail.get("message", ['no msg'])[0]
        response.data["status"] = exc.detail.get("status", ['no status'])[0]
    return response
