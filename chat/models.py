from django.db import models
from django.conf import settings
from django.utils import timezone

class DirectMessage(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    image = models.ImageField(upload_to='dm_photos/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"DM from {self.sender.username} to {self.recipient.username}: {self.message[:30]}"

class ChatSession(models.Model):
    """Track active chat sessions between users"""
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chat_sessions_1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chat_sessions_2', on_delete=models.CASCADE)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user1', 'user2']
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"
    
    @classmethod
    def get_or_create_session(cls, user1, user2):
        """Get existing session or create new one"""
        # Ensure consistent ordering of users
        if user1.id > user2.id:
            user1, user2 = user2, user1
        
        session, created = cls.objects.get_or_create(
            user1=user1,
            user2=user2,
            defaults={'is_active': True}
        )
        
        if not created:
            session.is_active = True
            session.save(update_fields=['is_active', 'last_activity'])
        
        return session
    
    def get_other_user(self, current_user):
        """Get the other user in the chat session"""
        return self.user2 if self.user1 == current_user else self.user1 