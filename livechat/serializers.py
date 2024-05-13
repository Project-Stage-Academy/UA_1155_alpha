from livechat.models import DirectChatBetweenUsers
from rest_framework_mongoengine.serializers import DocumentSerializer


class DirectChatBetweenUsersSerializer(DocumentSerializer):

    class Meta:
        model = DirectChatBetweenUsers
        fields = ["text"]
