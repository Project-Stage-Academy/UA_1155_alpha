from django.urls import path
from livechat.views import ChatsViewSet, room

urlpatterns = [
    path("", ChatsViewSet.as_view({'post': 'retrieve_or_create'}), name="chats-create"),
    path("room/<str:chat_name>/", room, name="room")
]
