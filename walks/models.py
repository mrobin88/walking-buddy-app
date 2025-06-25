from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils import timezone
import uuid


class Walk(models.Model):
    """Model for tracking walking sessions."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    TAG_CHOICES = [
        ('nature', 'Nature'),
        ('city', 'City'),
        ('historical', 'Historical'),
        ('scenic', 'Scenic'),
        ('exercise', 'Exercise'),
        ('social', 'Social'),
        ('exploration', 'Exploration'),
    ]
    
    # Basic info
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    # Route information (simplified)
    start_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    start_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    end_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    end_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Walk details
    distance = models.DecimalField(max_digits=8, decimal_places=3, default=0.0)  # in km
    duration = models.PositiveIntegerField(default=0)  # in minutes
    pace = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # min/km
    
    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    
    # Weather (optional)
    weather_temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    weather_conditions = models.CharField(max_length=100, blank=True)
    weather_humidity = models.PositiveIntegerField(blank=True, null=True)
    
    # Status and tags
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    tags = models.JSONField(default=list, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'walks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Walk {self.public_id} - {self.title or 'Untitled'}"
    
    def save(self, *args, **kwargs):
        """Calculate pace when saving."""
        if self.distance and self.duration:
            self.pace = self.duration / float(self.distance)
        super().save(*args, **kwargs)
    
    def get_participants(self):
        """Get all participants for this walk."""
        return self.participants.all()
    
    def add_participant(self, user, joined_at=None):
        """Add a participant to the walk."""
        from .models import WalkParticipant
        participant, created = WalkParticipant.objects.get_or_create(
            walk=self,
            user=user,
            defaults={'joined_at': joined_at}
        )
        return participant
    
    def remove_participant(self, user):
        """Remove a participant from the walk."""
        try:
            participant = self.participants.get(user=user)
            participant.left_at = timezone.now()
            participant.save()
            return True
        except WalkParticipant.DoesNotExist:
            return False
    
    def complete_walk(self, end_lat=None, end_lon=None, distance=None, duration=None):
        """Mark walk as completed."""
        self.status = 'completed'
        self.end_time = timezone.now()
        
        if end_lat is not None and end_lon is not None:
            self.end_latitude = end_lat
            self.end_longitude = end_lon
        if distance:
            self.distance = distance
        if duration:
            self.duration = duration
        
        self.save()
        
        # Update participant stats
        for participant in self.participants.all():
            if participant.user:
                participant.user.update_walk_stats(
                    float(self.distance), 
                    self.duration
                )


class WalkParticipant(models.Model):
    """Model for walk participants."""
    
    walk = models.ForeignKey(Walk, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='walks_participated')
    
    # Timing
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(blank=True, null=True)
    
    # Rating and review
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, null=True
    )
    review = models.TextField(max_length=500, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'walk_participants'
        unique_together = ['walk', 'user']
    
    def __str__(self):
        return f"{self.user.username} in {self.walk}"


class WalkPhoto(models.Model):
    """Model for photos taken during walks."""
    
    walk = models.ForeignKey(Walk, on_delete=models.CASCADE, related_name='photos')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='walk_photos')
    
    # Photo details
    image = models.ImageField(upload_to='walk_photos/')
    caption = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'walk_photos'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Photo by {self.uploaded_by.username} in {self.walk}"


class WalkChatMessage(models.Model):
    """Model for chat messages during walks."""
    
    walk = models.ForeignKey(Walk, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='walk_messages')
    
    # Message content
    message = models.TextField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'walk_chat_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}..."