from rest_framework import serializers
from .models import Ad

class AdSerializer(serializers.ModelSerializer):
    """Serializer for advertisements."""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Ad
        fields = [
            'id', 'user', 'title', 'description', 'image', 'image_url',
            'location', 'category', 'price', 'is_promoted', 'created_at',
            'updated_at', 'views', 'clicks', 'status'
        ]
        read_only_fields = ['image_url', 'views', 'clicks', 'status']
    
    def get_image_url(self, obj):
        """Get the URL for the ad image."""
        if obj.image:
            return obj.image.url
        return None

    def validate(self, data):
        """Validate ad data."""
        if not data.get('title'):
            raise serializers.ValidationError('Title is required.')
        if not data.get('description'):
            raise serializers.ValidationError('Description is required.')
        
        # Validate category
        valid_categories = ['walks', 'events', 'services', 'other']
        if data.get('category') not in valid_categories:
            raise serializers.ValidationError(
                f'Invalid category. Must be one of: {", ".join(valid_categories)}'
            )
        
        return data

    def create(self, validated_data):
        """Create a new ad."""
        # Get user's location
        user = validated_data['user']
        validated_data['location'] = {
            'lat': user.latitude,
            'lon': user.longitude
        }
        
        # Set default status
        validated_data['status'] = 'active'
        
        return super().create(validated_data)
