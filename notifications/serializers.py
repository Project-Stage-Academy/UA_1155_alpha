from rest_framework_mongoengine.serializers import DocumentSerializer

from notifications.models import Notification


class NotificationSerializer(DocumentSerializer):
    class Meta:
        model = Notification
        fields = ["project_id", "send_at", "text"]

