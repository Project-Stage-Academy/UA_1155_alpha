import jwt
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from .models import Chats
from users.models import CustomUser
from forum.settings import SECRET_KEY


def encode_jwt(id, first_name, last_name):
    payload = {'id': id, 'first_name': first_name, 'last_name': last_name}
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def get_user(user_id):
    try:
        return CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return AnonymousUser()


class ChatsViewSet(viewsets.ViewSet):
    def retrieve_or_create(self, request):

        sender_id = request.user.id
        sender_jwt_token = request.META.get('HTTP_AUTHORIZATION').split()[1]

        receiver_id = request.data.get('receiver_id')

        existing_chat = Chats.objects.filter(users_id=sender_id).filter(users_id=receiver_id).first()
        if existing_chat:
            chat_id = existing_chat.id
            chat_name = existing_chat.chat_name

        else:
            sender = get_object_or_404(CustomUser, pk=sender_id)
            receiver = get_object_or_404(CustomUser, pk=receiver_id)

            chat = Chats.objects.create(chat_name=f"room_{sender_id}_{receiver_id}")
            chat_name = chat.chat_name
            chat.users_id.add(sender)
            chat.users_id.add(receiver)
            chat_id = chat.id
        current_site = get_current_site(request).domain
        chat_url = f"{current_site}/api/livechat/room/{chat_name}/?token={sender_jwt_token}"

        response_data = {
            'chat_id': chat_id,
            'chat_name': chat_name,
            'chat_url': chat_url
        }

        return Response(response_data, status=status.HTTP_200_OK)


def room(request, chat_name):
    token = request.GET.get('token')
    chat = get_object_or_404(Chats, chat_name=chat_name)
    try:
        access_token = AccessToken(token)
        user = get_user(access_token["user_id"])
    except TokenError:
        user = AnonymousUser()

    if user not in chat.users_id.all():
        return HttpResponse(status=404)
    return render(request, 'livechat/lobby.html', {
        'chat_name': chat_name,
        'token': token,
        'username': f'{user.first_name} {user.last_name}',
        'sender_id': f'{user.id}'
    })
