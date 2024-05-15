import datetime
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from livechat.models import Livechat

from .models import Chats


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
        chat = await self.get_chat_object(self.room_name)
        if not chat:
            await self.close()

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Відключитися від групи кімнати
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Отримати повідомлення від WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message")
        username = text_data_json.get("username")
        timestamp = text_data_json.get("timestamp")

        # Відправити повідомлення у групу кімнати
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message,
                "username": username,
                "timestamp": timestamp,
            },
        )

    async def chat_message(self, event):
        # Отримати повідомлення з групи кімнати
        message = event["message"]

        # Зберегти повідомлення у базі даних
        Livechat.create_message(
            sender_id=self.user.id,
            room_name=self.scope["url_route"]["kwargs"]["room_name"],
            text=message,
        )
        print(self.user.id)

        # Відправити повідомлення у WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat",
                    "message": message,
                    "username": self.username,
                    "timestamp": str(datetime.datetime.now()),
                }
            )
        )

    @database_sync_to_async
    def get_chat_object(self, room_name):
        return Chats.objects.filter(chat_name=room_name).first()
