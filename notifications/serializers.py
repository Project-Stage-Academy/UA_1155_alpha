from rest_framework_mongoengine.serializers import DocumentSerializer

from notifications.models import Notification


class NotificationSerializer(DocumentSerializer):
    class Meta:
        model = Notification
        fields = ["is_read", "project_id", "send_at", "text"]

