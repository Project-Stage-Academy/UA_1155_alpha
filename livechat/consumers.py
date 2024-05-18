import datetime
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from livechat.models import Livechat, Status, LastLogin
from .models import Chats
from users.models import CustomUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        # Отримати ім'я кімнати з URL
        self.first_name = self.scope["user"].first_name
        self.last_name = self.scope["user"].last_name
        self.username = f"{self.first_name} {self.last_name}"
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Приєднатися до групи кімнати
        self.chat = await self.get_chat_object(self.room_name)
        if not self.chat:
            await self.close()

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        await self.update_last_login()
        await self.send_status("Online")
        statuses = Status.objects.filter(room_name=self.room_name)
        for status in statuses:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "status_update",
                    "user_id": status.user_id,
                    "status": status.status
                }
            )

        history = self.get_chat_history(self.room_name)
        for message in history:
            sender_id = message.sender_id
            username = await self.get_username(sender_id)

            await self.send(text_data=json.dumps({
                "message": message.text,
                "username": username,
                "timestamp": message.send_at.strftime("%m/%d/%Y, %H:%M:%S"),
                "type": "chat_history"
            }))

    async def send_status(self, status):
        await self.update_users_status(status)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "status_update",
                "user_id": self.user.id,
                "status": status
            }
        )

    async def update_last_login(self):
        last_login = LastLogin.objects.filter(room_name=self.room_name, user_id=self.user.id).first()
        if last_login:
            last_login.last_seen = datetime.datetime.now()
            last_login.save()
        else:
            LastLogin.objects.create(room_name=self.room_name, user_id=self.user.id, last_seen=datetime.datetime.now())


    @database_sync_to_async
    def update_users_status(self, status_arg):
        if Status.objects.filter(room_name=self.room_name, user_id=self.user.id):
            status = Status.objects.get(room_name=self.room_name, user_id=self.user.id)
            status.status = status_arg
            status.save()
        else:
            status = Status.objects.create(room_name=self.room_name, user_id=self.user.id, status=status_arg)
            status.save()

    @database_sync_to_async
    def get_participant_status(self, participant):
        status = Status.objects.get(room_name=self.room_name, user_id=participant.id)
        return status

    async def status_update(self, event):
        user_id = event["user_id"]
        status = event["status"]
        await self.send(
            text_data=json.dumps(
                {
                    "type": "status_update",
                    "user_id": user_id,
                    "status": status
                }
            )
        )

    async def disconnect(self, close_code):
        # Відключитися від групи кімнати
        await self.send_status("Offline")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def receive(self, text_data=None, bytes_data=None):
        # Отримати повідомлення від WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message")
        sender_id = text_data_json.get("sender_id")
        username = text_data_json.get("username")
        timestamp = text_data_json.get("timestamp")

        await self.save_message(message)

        # Відправити повідомлення у групу кімнати
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message,
                "username": username,
                "timestamp": timestamp,
                "sender_id": sender_id,

            },
        )

    async def save_message(self, message):
        # Зберегти повідомлення у базі даних
        await database_sync_to_async(Livechat.create_message)(
            sender_id=self.user.id,
            room_name=self.scope["url_route"]["kwargs"]["room_name"],
            text=message,
        )

    async def chat_message(self, event):
        # Отримати повідомлення з групи кімнати
        message = event["message"]
        username = event["username"]
        sender_id = event["sender_id"]

        # Відправити повідомлення у WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat",
                    "message": message,
                    "username": username,
                    "sender_id": sender_id,
                    "timestamp": str(datetime.datetime.now()),
                    "user_id": self.user.id,
                }
            )
        )

    @database_sync_to_async
    def get_chat_object(self, room_name):
        return Chats.objects.filter(chat_name=room_name).first()

    def get_chat_history(self, room_name):
        return Livechat.objects.filter(room_name=room_name)

    @database_sync_to_async
    def get_username(self, sender_id):
        user = CustomUser.objects.filter(id=sender_id).first()
        if user:
            return f"{user.first_name} {user.last_name}"
        return None

    @database_sync_to_async
    def get_chat_participants(self):
        return self.chat.users_id.all()

