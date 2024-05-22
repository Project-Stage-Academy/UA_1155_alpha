import mongoengine
from datetime import datetime
from django.db import models
from users.models import CustomUser


class Chats(models.Model):
    chat_name = models.CharField(max_length=255)
    users_id = models.ManyToManyField("users.CustomUser", related_name="chats")

    class Meta:
        db_table = "chats"


class Livechat(mongoengine.Document):
    sender_id = mongoengine.IntField(required=True)
    room_name = mongoengine.StringField(required=True, max_length=100)
    send_at = mongoengine.DateTimeField(default=datetime.now)
    is_read = mongoengine.BooleanField(default=False)
    text = mongoengine.StringField(blank=True, null=True, max_length=2000)
    image = mongoengine.ImageField(blank=True, null=True)

    @classmethod
    def create_message(cls, sender_id, room_name, text):
        message = cls(
            sender_id=sender_id,
            room_name=room_name,
            text=text,
        )
        message.save()
        return message


class Status(mongoengine.Document):
    room_name = mongoengine.StringField(required=True)
    user_id = mongoengine.IntField(required=True)
    status = mongoengine.StringField()


class LastLogin(mongoengine.Document):
    room_name = mongoengine.StringField(required=True)
    user_id = mongoengine.IntField(required=True)
    last_seen = mongoengine.DateTimeField(default=datetime.now)
