from datetime import datetime

import mongoengine
from django.db import models
from users.models import CustomUser


class Chats(models.Model):
    chat_name = models.CharField(max_length=255)
    users_id = models.ManyToManyField("users.CustomUser", related_name="chats")

    class Meta:
        db_table = "chats"


class Livechat(mongoengine.Document):

    sender_id = mongoengine.IntField(required=True)
    room_name = mongoengine.IntField(required=True)
    send_at = mongoengine.DateTimeField(default=datetime.now)
    is_read = mongoengine.BooleanField(default=False)
    text = mongoengine.StringField(required=True, max_length=2000)

    @classmethod
    def create_message(cls, sender_id, room_name, text):
        message = cls(
            sender_id=sender_id,
            room_name=room_name,
            text=text,
        )
        message.save()
        return message
