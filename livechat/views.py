from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Chats
from users.models import CustomUser


class ChatsViewSet(viewsets.ViewSet):
    def create(self, request):
        sender_id = request.data.get('sender_id')
        receiver_id = request.data.get('receiver_id')
        chat_name = request.data.get('chat_name')

        existing_chat = Chats.objects.filter(users_id=sender_id).filter(users_id=receiver_id).first()
        if existing_chat:
            chat_id = existing_chat.id
            return Response({'chat_id': chat_id}, status=status.HTTP_200_OK)

        sender = get_object_or_404(CustomUser, pk=sender_id)
        receiver = get_object_or_404(CustomUser, pk=receiver_id)

        chat = Chats.objects.create(chat_name=chat_name)
        chat.users_id.add(sender)
        chat.users_id.add(receiver)
        chat_id = chat.id
        return Response({'chat_id': chat_id}, status=status.HTTP_201_CREATED)