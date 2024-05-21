import mongoengine
from datetime import datetime


class Notification(mongoengine.Document):
    TYPES_OF_RECIPIENTS = [
        ("investor", "Investor"),
        ("startup", "Startup"),
        ("project", "Project")
    ]

    recipient_id = mongoengine.IntField(required=True)
    recipient_type = mongoengine.StringField(choices=TYPES_OF_RECIPIENTS)
    send_at = mongoengine.DateTimeField(default=datetime.now)
    text = mongoengine.StringField(required=True, max_length=1000)

    meta = {
        'allow_inheritance': True
    }

    @classmethod
    def create_notification(cls, recipient_type, recipient_id, text):
        notification = cls(
            recipient_type=recipient_type,
            recipient_id=recipient_id,
            text=text
        )
        notification.save()
        return notification


class ProjectNotification(Notification):
    TYPES_OF_NOTIFICATIONS = [
        ("project_updating", "Project Updating"),
        ("investor_subscription", "Investors Subscription"),
    ]

    project_id = mongoengine.IntField(required=True)
    type_of_notification = mongoengine.StringField(choices=TYPES_OF_NOTIFICATIONS)
    is_read = mongoengine.BooleanField(default=False)

    @classmethod
    def create_notification(cls, recipient_type, recipient_id, project_id, type_of_notification, text):
        notification = cls(
            recipient_type=recipient_type,
            recipient_id=recipient_id,
            project_id=project_id,
            type_of_notification=type_of_notification,
            text=text
        )
        notification.save()
        return notification

    @staticmethod
    def get_unread_notifications(recipient_id, is_read=False):
        notifications = ProjectNotification.objects.filter(recipient_id=recipient_id, is_read=is_read).order_by(
            '-send_at')
        return notifications

    @staticmethod
    def get_all_notifications(recipient_id):
        notifications = ProjectNotification.objects.filter(recipient_id=recipient_id).order_by('-send_at')
        return notifications
