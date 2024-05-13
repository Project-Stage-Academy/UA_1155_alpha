from django.urls import path
from livechat.views import ChatsViewSet


urlpatterns = [
    path("", ChatsViewSet.as_view({'post': 'retrieve_or_create'}), name="chats-create"),
]