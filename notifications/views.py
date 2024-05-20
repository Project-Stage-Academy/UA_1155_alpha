from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.models import Notification
from .serializers import NotificationSerializer
from .tasks import send_approve, send_decline
from .utils import get_model_by_name


class NotificationsViewSet(viewsets.ViewSet):
    """
    ViewSet for viewing notifications.

    The ViewSet provides two `get` actions for viewing new (unread) notifications
    and all notification for each user.

    Available methods:
    - GET: Returns a list of all unread notifications (GET /api/notifications/new/)
    - GET: Returns a list of all notifications (GET /api/notifications/all)

    Parameters:
    - request: The request object, containing request data and parameters.

    Request/Response Formats:
    - Methods accept data in JSON format and also return responses in JSON format.
    - Responses contain the status of the operation, messages, and project data (in list, retrieve, create, update,
      partial_update operations).
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='new')
    def get_my_new_notifications(self, request):
        """
        Retrieve and mark as read all new (unread) notifications for the current user.

        Args:
            self: The view instance.
            request: The request object.

        Returns:
            Response: A JSON response containing a list of new notifications.
        """
        user = request.user

        notifications = Notification.get_unread_notifications(recipient_id=user.id, is_read=False)

        if not notifications:
            return Response({"message": "You do not have new notifications."}, status=status.HTTP_404_NOT_FOUND)
        serializer = NotificationSerializer(notifications, many=True)
        for notification in notifications:
            notification.is_read = True
            notification.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='all')
    def get_my_all_notifications(self, request):
        """
        Retrieve all notifications for the current user.

        Args:
            self: The view instance.
            request: The request object.

        Returns:
            Response: A JSON response containing a list of all notifications.
        """
        user = request.user

        notifications = Notification.get_all_notifications(recipient_id=user.id)

        if not notifications:
            return Response({"message": "You do not have new notifications."}, status=status.HTTP_404_NOT_FOUND)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def approve(request, model_name, data_id):
    model = get_model_by_name(model_name)
    instance = model.objects.get(pk=data_id)

    instance.is_verified = True
    instance.save()

    if model_name == 'Project':
        contact_email = instance.startup.contact_email
    else:
        contact_email = instance.contact_email

    send_approve(model_name, contact_email)
    return HttpResponse(f"{model_name} profile #{data_id} passed moderation approval")


def decline(request, model_name, data_id):
    model = get_model_by_name(model_name)
    instance = model.objects.get(pk=data_id)

    if model_name == 'Project':
        contact_email = instance.startup.contact_email
    else:
        contact_email = instance.contact_email

    send_decline(model_name, contact_email)
    return HttpResponse(f"{model_name} profile #{data_id} did not pass moderation approval")
