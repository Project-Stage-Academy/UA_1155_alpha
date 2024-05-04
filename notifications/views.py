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
        notifications = []
        user = request.user

        if user.is_investor:
            investor_notifications = Notification.objects.filter(recipient_id=user.id, recipient_type="investor",
                                                                 is_read=False)
            notifications.extend(investor_notifications)
            investor_notifications.update(is_read=True)
        if user.is_startup:
            startup_notifications = Notification.objects.filter(recipient_id=user.id, recipient_type="startup",
                                                                is_read=False)
            notifications.extend(startup_notifications)
            startup_notifications.update(is_read=True)

        if not notifications:
            return Response({"message": "You do not have new notifications."}, status=status.HTTP_404_NOT_FOUND)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


