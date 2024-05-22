import datetime
import json
import base64
from io import BytesIO
from PIL import Image

from django.core.files.base import ContentFile
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from livechat.models import LastLogin, Livechat, Status
from users.models import CustomUser

from .models import Chats


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.first_name = self.scope["user"].first_name
        self.last_name = self.scope["user"].last_name
        self.username = f"{self.first_name} {self.last_name}"
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

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
                    "status": status.status,
                },
            )

        history = self.get_chat_history(self.room_name)
        for message in history:
            sender_id = message.sender_id
            username = await self.get_username(sender_id)
            if message.image:
                image = Image.open(BytesIO(message.image.read()))
                image_bytes = BytesIO()
                image.save(image_bytes, format=image.format)
                image_data = image_bytes.getvalue()

                image_base64 = base64.b64encode(image_data).decode('utf-8')
                data_to_send = {
                    "image": image_base64,
                    "username": username,
                    "timestamp": message.send_at.strftime("%m/%d/%Y, %H:%M:%S"),
                    "type": "chat_history",
                    "sender_id": message.sender_id,
                }
            elif message.audio:
                audio_data = message.audio.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                data_to_send = {
                    "audio": audio_base64,
                    "text": message.text,
                    "username": username,
                    "timestamp": message.send_at.strftime("%m/%d/%Y, %H:%M:%S"),
                    "type": "chat_history",
                    "sender_id": message.sender_id,
                }
            else:
                data_to_send = {
                    "message": message.text,
                    "username": username,
                    "timestamp": message.send_at.strftime("%m/%d/%Y, %H:%M:%S"),
                    "type": "chat_history",
                    "sender_id": message.sender_id,
                }
            await self.send(
                text_data=json.dumps(data_to_send)
            )

    async def send_status(self, status):
        await self.update_users_status(status)
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "status_update", "user_id": self.user.id, "status": status},
        )

    async def update_last_login(self):
        last_login = LastLogin.objects.filter(
            room_name=self.room_name, user_id=self.user.id
        ).first()
        if last_login:
            last_login.last_seen = datetime.datetime.now()
            last_login.save()
        else:
            LastLogin.objects.create(
                room_name=self.room_name,
                user_id=self.user.id,
                last_seen=datetime.datetime.now(),
            )

    @database_sync_to_async
    def update_users_status(self, status_arg):
        if Status.objects.filter(room_name=self.room_name, user_id=self.user.id):
            status = Status.objects.get(room_name=self.room_name, user_id=self.user.id)
            status.status = status_arg
            status.save()
        else:
            status = Status.objects.create(
                room_name=self.room_name, user_id=self.user.id, status=status_arg
            )
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
                {"type": "status_update", "user_id": user_id, "status": status}
            )
        )

    async def disconnect(self, close_code):
        await self.send_status("Offline")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        type = text_data_json.get("type")
        if type == "image":
            image_data = text_data_json.get('file')
            if image_data:
                image_bytes = base64.b64decode(image_data)
                sender_id = text_data_json.get("sender_id")
                username = text_data_json.get("username")
                timestamp = text_data_json.get("timestamp")

                await self.save_image(image_bytes)

                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat.image",
                        "image": image_base64,  # Отправляем обратно байты изображения
                        "sender_id": sender_id,
                        "username": username,
                        "timestamp": timestamp,
                    },
                )
        elif type == "audio":
            file_data = text_data_json.get('file')
            if file_data:
                file_bytes = base64.b64decode(file_data)
                text = text_data_json.get("name")
                sender_id = text_data_json.get("sender_id")
                username = text_data_json.get("username")
                timestamp = text_data_json.get("timestamp")

                await self.save_audio(file_bytes, text)
                file_base64 = base64.b64encode(file_bytes).decode('utf-8')
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat.audio",
                        "text": text,
                        "audio": file_base64,
                        "sender_id": sender_id,
                        "username": username,
                        "timestamp": timestamp,
                    },
                )
        else:
            message = text_data_json.get("message")
            sender_id = text_data_json.get("sender_id")
            username = text_data_json.get("username")
            timestamp = text_data_json.get("timestamp")

            await self.save_message(message)

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

    async def save_image(self, image_bytes):
        image_name = f"{self.room_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        image = ContentFile(image_bytes, name=image_name)
        await database_sync_to_async(Livechat.create_message)(
            sender_id=self.user.id,
            room_name=self.scope["url_route"]["kwargs"]["room_name"],
            image=image,
        )

    async def save_message(self, message):
        await database_sync_to_async(Livechat.create_message)(
            sender_id=self.user.id,
            room_name=self.scope["url_route"]["kwargs"]["room_name"],
            text=message,
        )

    async def save_audio(self, audio_bytes, text):
        file_name = f"{self.room_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
        file = ContentFile(audio_bytes, name=file_name)
        await database_sync_to_async(Livechat.create_message)(
            sender_id=self.user.id,
            room_name=self.scope["url_route"]["kwargs"]["room_name"],
            audio=file,
            text=text
        )

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        sender_id = event["sender_id"]

        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat",
                    "message": message,
                    "username": username,
                    "sender_id": sender_id,
                    "timestamp": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                }
            )
        )


    async def chat_image(self, event):
        image_bytes = event["image"]
        sender_id = event["sender_id"]
        username = event["username"]

        await self.send(
            text_data=json.dumps(
                {
                    "type": "image",
                    "image": image_bytes,
                    "sender_id": sender_id,
                    "username": username,
                    "timestamp": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                }
            )
        )

    async def chat_audio(self, event):
        audio_bytes = event["audio"]
        sender_id = event["sender_id"]
        username = event["username"]
        text = event["text"]

        await self.send(
            text_data=json.dumps(
                {
                    "type": "audio",
                    "audio": audio_bytes,
                    "text": text,
                    "sender_id": sender_id,
                    "username": username,
                    "timestamp": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
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
