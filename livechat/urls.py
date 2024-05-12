from django.urls import path
from livechat.views import ChatsViewSet


urlpatterns = [
    path("", ChatsViewSet.as_view({'post': 'create'}), name="chats-create"),
]