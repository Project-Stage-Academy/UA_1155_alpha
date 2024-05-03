import mongoengine

from datetime import datetime


class Notification(mongoengine.Document):
    TYPES_OF_NOTIFICATIONS = [
        ("project_updating", "Project Updating"),
        ("investor_subscription", "Investors Subscription"),
        ("new_message", "New Message")
    ]

    investor_id = mongoengine.IntField(required=True)
    project_id = mongoengine.IntField(required=True)
    type_of_notification = mongoengine.StringField(choices=TYPES_OF_NOTIFICATIONS)
    send_at = mongoengine.DateTimeField(default=datetime.now)
    is_read = mongoengine.BooleanField(default=False)
    text = mongoengine.StringField(required=True, max_length=1000)
