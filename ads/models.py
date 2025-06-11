from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AdEvent(models.Model):
    """Track ad impressions and clicks."""
    EVENT_TYPES = [
        ('impression', 'Impression'),
        ('click', 'Click'),
    ]
    
    AD_PLACEMENTS = [
        ('homepage', 'Homepage'),
        ('chat', 'Chat'),
        ('profile', 'Profile'),
        ('sidebar', 'Sidebar'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    placement = models.CharField(max_length=20, choices=AD_PLACEMENTS)
    ad_id = models.CharField(max_length=100)
    revenue = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ad_events'
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['placement', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.placement} - {self.created_at}"


class AdCampaign(models.Model):
    """Manage ad campaigns and their performance."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ad_campaigns'
    
    def __str__(self):
        return self.name
    
    @property
    def total_impressions(self):
        return self.ad_events.filter(event_type='impression').count()
    
    @property
    def total_clicks(self):
        return self.ad_events.filter(event_type='click').count()
    
    @property
    def click_through_rate(self):
        if self.total_impressions == 0:
            return 0
        return (self.total_clicks / self.total_impressions) * 100 