import datetime
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from livechat.models import Livechat
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
        chat = await self.get_chat_object(self.room_name)
        if not chat:
            await self.close()

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

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


    async def disconnect(self, close_code):
        # Відключитися від групи кімнати
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
        sender_id=event["sender_id"]

        # Відправити повідомлення у WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat",
                    "message": message,
                    "username": username,
                    "sender_id": sender_id,
                    "timestamp": str(datetime.datetime.now()),
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







    # async def chat_message(self, event):
    #     # Отримати повідомлення з групи кімнати
    #     message = event["message"]

    #     # Перевірити, чи повідомлення вже збережене в базі даних
    #     if not await self.is_message_saved(message):
    #         # Зберегти повідомлення у базі даних
    #         await Livechat.create_message(
    #             sender_id=self.user.id,
    #             room_name=self.scope["url_route"]["kwargs"]["room_name"],
    #             text=message,
    #         )

    #     # Відправити повідомлення у WebSocket
    #     await self.send(
    #         text_data=json.dumps(
    #             {
    #                 "type": "chat",
    #                 "message": message,
    #                 "username": self.username,
    #                 "timestamp": str(datetime.datetime.now()),
    #             }
    #         )
    #     )

    # @database_sync_to_async
    # def is_message_saved(self, message):
    #     # Перевірити, чи повідомлення вже збережене в базі даних
    #     return Livechat.objects.filter(
    #         sender_id=self.user.id,
    #         room_name=self.scope["url_route"]["kwargs"]["room_name"],
    #         text=message,
    #     ).first()
