from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Friendship


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'bio', 'walking_pace',
            'preferred_distance', 'interests'
        ]
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        """Create a new user."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        """Validate user credentials."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            try:
                # Find user by email only
                user = User.objects.get(email=email)
                # Authenticate with the email
                user = authenticate(username=email, password=password)
                
                if not user:
                    raise serializers.ValidationError('Invalid credentials.')
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                
                # Return the user object
                return {'user': user}
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid credentials.')
        
        raise serializers.ValidationError('Must include identifier and password.')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    
    class Meta:
        model = User
        fields = [
            'id', 'public_id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'profile_picture', 'walking_pace', 'preferred_distance',
            'interests', 'total_walks', 'total_distance', 'total_time',
            'average_rating', 'total_ratings', 'is_online', 'last_active'
        ]
        read_only_fields = [
            'id', 'public_id', 'username', 'email', 'total_walks', 'total_distance',
            'total_time', 'average_rating', 'total_ratings', 'is_online', 'last_active'
        ]


class UserStatsSerializer(serializers.ModelSerializer):
    """Serializer for user statistics."""
    
    class Meta:
        model = User
        fields = [
            'total_walks', 'total_distance', 'total_time',
            'average_rating', 'total_ratings'
        ]


class UserLocationSerializer(serializers.ModelSerializer):
    """Serializer for updating user location."""
    
    class Meta:
        model = User
        fields = ['latitude', 'longitude']
    
    def update(self, instance, validated_data):
        """Update user location."""
        latitude = validated_data.get('latitude')
        longitude = validated_data.get('longitude')
        if latitude is not None and longitude is not None:
            instance.update_location(latitude, longitude)
        return instance





class FriendshipSerializer(serializers.ModelSerializer):
    """Serializer for friendship relationships."""
    from_user = UserProfileSerializer(read_only=True)
    to_user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ['id', 'from_user', 'to_user', 'created_at', 'accepted'] 