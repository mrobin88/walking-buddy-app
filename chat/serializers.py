from rest_framework import serializers
from .models import DirectMessage
from users.serializers import UserProfileSerializer
from users.models import User

class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'profile_picture', 'walking_pace', 'preferred_distance', 'latitude', 'longitude']

class DirectMessageSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True)
    recipient = UserProfileSerializer(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = DirectMessage
        fields = ['id', 'sender', 'recipient', 'message', 'image', 'timestamp', 'read']
        read_only_fields = ['id', 'sender', 'timestamp', 'read']