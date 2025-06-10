from rest_framework import serializers
from .models import DirectMessage
from users.serializers import UserProfileSerializer

class DirectMessageSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True)
    recipient = UserProfileSerializer(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = DirectMessage
        fields = ['id', 'sender', 'recipient', 'message', 'image', 'timestamp', 'read']
        read_only_fields = ['id', 'sender', 'timestamp', 'read'] 