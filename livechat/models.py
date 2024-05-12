from django.db import models
from users.models import CustomUser

class Chats(models.Model):
    chat_name = models.CharField(max_length=255)
    users_id = models.ManyToManyField("users.CustomUser", related_name='chats')


    class Meta:
        db_table = 'chats'

