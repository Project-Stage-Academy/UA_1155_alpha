from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from notifications.models import Notification
from .serializers import NotificationSerializer
from rest_framework.decorators import action


class NotificationsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='new')
    def get_my_new_notifications(self, request):
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
        user = request.user

        notifications = Notification.get_all_notifications(recipient_id=user.id)

        if not notifications:
            return Response({"message": "You do not have new notifications."}, status=status.HTTP_404_NOT_FOUND)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
