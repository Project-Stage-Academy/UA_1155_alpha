from datetime import datetime

import mongoengine
from django.db import models
from users.models import CustomUser


class Chats(models.Model):
    chat_name = models.CharField(max_length=255)
    users_id = models.ManyToManyField("users.CustomUser", related_name="chats")

    class Meta:
        db_table = "chats"


class DirectChatBetweenUsers(mongoengine.Document):

    from_user = mongoengine.IntField(required=True)
    to_user = mongoengine.IntField(required=True)
    project_id = mongoengine.IntField(required=True)
    send_at = mongoengine.DateTimeField(default=datetime.now)
    is_read = mongoengine.BooleanField(default=False)
    text = mongoengine.StringField(required=True, max_length=1000)

    @classmethod
    def create_message(cls, from_user, to_user, project_id, text):
        message = cls(
            from_user=from_user, to_user=to_user, project_id=project_id, text=text
        )
        message.save()
        return message
