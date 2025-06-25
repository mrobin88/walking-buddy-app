from django.db import models
from django.utils import timezone
from django.db.models import JSONField
from users.models import User

# Ad categories
AD_CATEGORIES = [
    ('walks', 'Walking Groups'),
    ('events', 'Events'),
    ('services', 'Services'),
    ('other', 'Other')
]

# Ad statuses
AD_STATUSES = [
    ('draft', 'Draft'),
    ('active', 'Active'),
    ('expired', 'Expired')
]

class Ad(models.Model):
    """Model for user advertisements."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    image = models.ImageField(upload_to='ad_images/', blank=True, null=True)
    location = JSONField(default=dict)  # Store lat/lon
    category = models.CharField(max_length=50, choices=AD_CATEGORIES)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_promoted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=AD_STATUSES, default='draft')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ad'
        verbose_name_plural = 'Ads'

    def __str__(self):
        return self.title

    def get_location(self):
        """Get the ad's location as a tuple of (lat, lon)."""
        return (self.location.get('lat', 0), self.location.get('lon', 0))

    def calculate_distance(self, user_location):
        """Calculate distance from user's location using Haversine formula."""
        from math import radians, sin, cos, sqrt, atan2
        
        if not user_location:
            return float('inf')
            
        lat1, lon1 = radians(user_location[0]), radians(user_location[1])
        lat2, lon2 = radians(self.location.get('lat', 0)), radians(self.location.get('lon', 0))
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        # Radius of Earth in kilometers
        R = 6371.0
        return R * c

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def increment_clicks(self):
        self.clicks += 1
        self.save(update_fields=['clicks'])

    def is_active(self):
        """Check if ad is active."""
        return self.status == 'active' and (not self.subscription_expiry or self.subscription_expiry > timezone.now())
