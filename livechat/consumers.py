import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Отримати ім'я кімнати з URL
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Приєднатися до групи кімнати
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Відключитися від групи кімнати
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        # Отримати повідомлення від WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')

        # Відправити повідомлення у групу кімнати
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': message
            }
        )

    async def chat_message(self, event):
        # Отримати повідомлення з групи кімнати
        message = event['message']

        # Відправити повідомлення у WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))