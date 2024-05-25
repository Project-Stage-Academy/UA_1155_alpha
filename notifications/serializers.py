from rest_framework_mongoengine.serializers import DocumentSerializer

from notifications.models import ProjectNotification


class ProjectNotificationSerializer(DocumentSerializer):
    class Meta:
        model = ProjectNotification
        fields = ["project_id", "send_at", "text"]

