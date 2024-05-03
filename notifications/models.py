import mongoengine

from datetime import datetime


class Notification(mongoengine.Document):
    TYPES_OF_NOTIFICATIONS = [
        ("project_updating", "Project Updating"),
        ("investor_subscription", "Investors Subscription"),
        ("new_message", "New Message")
    ]
    TYPES_OF_RECIPIENTS = [
        ("investor", "Investor"),
        ("startup", "Startup")
    ]

    recipient_id = mongoengine.IntField(required=True)
    recipient_type = mongoengine.StringField(choices=TYPES_OF_RECIPIENTS)
    project_id = mongoengine.IntField(required=True)
    type_of_notification = mongoengine.StringField(choices=TYPES_OF_NOTIFICATIONS)
    send_at = mongoengine.DateTimeField(default=datetime.now)
    is_read = mongoengine.BooleanField(default=False)
    text = mongoengine.StringField(required=True, max_length=1000)

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
