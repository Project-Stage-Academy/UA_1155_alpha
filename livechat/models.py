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

    recipient_id = mongoengine.IntField(required=True)
    recevier_id = mongoengine.IntField(required=True)
    chat_id = mongoengine.IntField(required=True)
    send_at = mongoengine.DateTimeField(default=datetime.now)
    is_read = mongoengine.BooleanField(default=False)
    text = mongoengine.StringField(required=True, max_length=2000)

    @classmethod
    def create_message(cls, recipient_id, recevier_id, chat_id, text):
        message = cls(
            recipient_id=recipient_id,
            recevier_id=recevier_id,
            chat_id=chat_id,
            text=text,
        )
        message.save()
        return message
