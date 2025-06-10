from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class User(AbstractUser):
    """Custom user model with extended profile and statistics."""
    
    # Basic profile fields
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # Walking preferences
    WALKING_PACE_CHOICES = [
        ('slow', 'Slow'),
        ('moderate', 'Moderate'),
        ('fast', 'Fast'),
    ]
    walking_pace = models.CharField(max_length=10, choices=WALKING_PACE_CHOICES, default='moderate')
    preferred_distance = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)  # in km
    
    # Interests
    INTEREST_CHOICES = [
        ('nature', 'Nature'),
        ('science', 'Science'),
        ('history', 'History'),
        ('art', 'Art'),
        ('music', 'Music'),
        ('sports', 'Sports'),
        ('technology', 'Technology'),
        ('food', 'Food'),
        ('travel', 'Travel'),
    ]
    interests = models.JSONField(default=list, blank=True)
    
    # Statistics
    total_walks = models.PositiveIntegerField(default=0)
    total_distance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # in km
    total_time = models.PositiveIntegerField(default=0)  # in minutes
    average_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_ratings = models.PositiveIntegerField(default=0)
    
    # Location (simplified)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    location_updated = models.DateTimeField(auto_now=True)
    
    # Status
    is_online = models.BooleanField(default=False)
    last_active = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # UUID for public identification
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_full_name() or 'No name'})"
    
    @property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def update_location(self, latitude, longitude):
        """Update user's location."""
        self.latitude = latitude
        self.longitude = longitude
        self.save(update_fields=['latitude', 'longitude', 'location_updated'])
    
    def update_walk_stats(self, distance, duration, rating=None):
        """Update user's walking statistics."""
        self.total_walks += 1
        self.total_distance += distance
        self.total_time += duration
        
        if rating is not None:
            total_rating = (self.average_rating * self.total_ratings) + rating
            self.total_ratings += 1
            self.average_rating = total_rating / self.total_ratings
        
        self.save(update_fields=[
            'total_walks', 'total_distance', 'total_time', 
            'average_rating', 'total_ratings'
        ])
    
    def to_dict(self):
        """Convert user to dictionary for API responses."""
        return {
            'id': self.public_id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'bio': self.bio,
            'profile_picture': self.profile_picture.url if self.profile_picture else None,
            'walking_pace': self.walking_pace,
            'preferred_distance': float(self.preferred_distance),
            'interests': self.interests,
            'stats': {
                'total_walks': self.total_walks,
                'total_distance': float(self.total_distance),
                'total_time': self.total_time,
                'average_rating': float(self.average_rating),
                'total_ratings': self.total_ratings,
            },
            'is_online': self.is_online,
            'last_active': self.last_active.isoformat() if self.last_active else None,
        }


class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='friendship_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friendship_requests_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')
        db_table = 'friendships'

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({'Accepted' if self.accepted else 'Pending'})" 