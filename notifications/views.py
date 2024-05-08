from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from notifications.models import Notification
from .serializers import NotificationSerializer


# Create your views here.
class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        notifications = Notification.get_unread_notifications(recipient_id=user.id, is_read=False)
        notifications.update(is_read=True)

        if not notifications:
            return Response({"message": "You do not have new notifications."}, status=status.HTTP_404_NOT_FOUND)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationsAllView(APIView):
    def get(self, request):
        user = request.user

        notifications = Notification.get_all_notifications(recipient_id=user.id)

        if not notifications:
            return Response({"message": "You do not have new notifications."}, status=status.HTTP_404_NOT_FOUND)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
