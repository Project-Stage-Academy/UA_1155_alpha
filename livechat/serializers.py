from livechat.models import Livechat
from rest_framework_mongoengine.serializers import DocumentSerializer


class DirectChatBetweenUsersSerializer(DocumentSerializer):

    class Meta:
        model = Livechat
        fields = ["text"]
