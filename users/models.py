from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.utils import timezone
from django.db.models import JSONField

# Premium subscription plans
SUBSCRIPTION_PLANS = [
    ('basic', 'Basic'),
    ('premium', 'Premium'),
    ('business', 'Business')
]

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
    
    # Premium features
    subscription_plan = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_PLANS,
        default='basic'
    )
    subscription_expiry = models.DateTimeField(null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    daily_chats_used = models.IntegerField(default=0)
    max_daily_chats = models.IntegerField(default=10)

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
    
    @property
    def has_premium(self):
        """Check if user has premium subscription."""
        return self.subscription_plan == 'premium' and (self.subscription_expiry is None or self.subscription_expiry > timezone.now())
    
    def update_location(self, latitude, longitude):
        """Update user's location and online status."""
        self.latitude = latitude
        self.longitude = longitude
        self.is_online = True
        self.last_active = timezone.now()
        self.save(update_fields=['latitude', 'longitude', 'location_updated', 'is_online', 'last_active'])
    
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
            'is_premium': self.is_premium,
        }


class Profile(models.Model):
    """Extended user profile with premium features."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_premium = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_expires = models.DateTimeField(null=True, blank=True)
    daily_chats_used = models.PositiveIntegerField(default=0)
    last_chat_reset = models.DateField(auto_now_add=True)
    profile_views = models.PositiveIntegerField(default=0)
    
    # Premium features tracking
    can_see_profile_views = models.BooleanField(default=False)
    can_hide_ads = models.BooleanField(default=False)
    extended_discovery_radius = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"{self.user.username} Profile ({'Premium' if self.is_premium else 'Free'})"
    
    def can_send_chat(self):
        """Check if user can send a chat message based on tier."""
        if self.is_premium:
            return True
        return self.daily_chats_used < 5
    
    def increment_chat_usage(self):
        """Increment daily chat usage."""
        if not self.is_premium:
            self.daily_chats_used += 1
            self.save(update_fields=['daily_chats_used'])
    
    def reset_daily_chats(self):
        """Reset daily chat count (called by management command)."""
        if not self.is_premium:
            self.daily_chats_used = 0
            self.save(update_fields=['daily_chats_used'])


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