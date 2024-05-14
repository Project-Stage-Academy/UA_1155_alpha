import uuid

from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Chats
from users.models import CustomUser


class ChatsViewSet(viewsets.ViewSet):
    def retrieve_or_create(self, request):
        sender_id = request.user.id
        receiver_id = request.data.get('receiver_id')

        existing_chat = Chats.objects.filter(users_id=sender_id).filter(users_id=receiver_id).first()
        if existing_chat:
            chat_id = existing_chat.id
            chat_name = existing_chat.chat_name

        else:
            sender = get_object_or_404(CustomUser, pk=sender_id)
            receiver = get_object_or_404(CustomUser, pk=receiver_id)

            chat = Chats.objects.create(chat_name=f"room_{sender_id}_{receiver_id}")
            chat.users_id.add(sender)
            chat.users_id.add(receiver)
            chat_id = chat.id
        current_site = get_current_site(request).domain
        chat_url = f"{current_site}/api/livechat/room/{chat_name}/"

        response_data = {
            'chat_id': chat_id,
            'chat_name': chat_name,
            'chat_url': chat_url
        }

        return Response(response_data, status=status.HTTP_200_OK)


def room(request, chat_name):
    return render(request, 'livechat/lobby.html', {
        'chat_name': chat_name
    })
