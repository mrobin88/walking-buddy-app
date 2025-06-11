#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_walking_buddy.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import User, Profile
from chat.models import DirectMessage
from walks.models import Walk, WalkParticipant, WalkChatMessage
from ads.models import AdEvent, AdCampaign

User = get_user_model()

def view_database_data():
    print("🔍 VIEWING DATABASE DATA")
    print("=" * 50)
    
    # Users
    print("\n👥 USERS:")
    users = User.objects.all()
    for user in users:
        print(f"  - {user.username} ({user.email}) - Online: {user.is_online}")
        if hasattr(user, 'profile'):
            print(f"    Premium: {user.profile.is_premium}, Daily chats: {user.profile.daily_chats_used}")
    
    # Walks
    print(f"\n🚶 WALKS ({Walk.objects.count()} total):")
    walks = Walk.objects.all()
    for walk in walks:
        print(f"  - {walk.title}")
        print(f"    Distance: {walk.distance}km, Duration: {walk.duration}min")
        print(f"    Status: {walk.status}, Participants: {walk.participants.count()}")
    
    # Walk Participants
    print(f"\n👥 WALK PARTICIPANTS ({WalkParticipant.objects.count()} total):")
    participants = WalkParticipant.objects.all()
    for participant in participants:
        print(f"  - {participant.user.username} in '{participant.walk.title}'")
        if participant.rating:
            print(f"    Rating: {participant.rating}/5")
    
    # Direct Messages
    print(f"\n💬 DIRECT MESSAGES ({DirectMessage.objects.count()} total):")
    messages = DirectMessage.objects.all()[:10]  # Show first 10
    for msg in messages:
        print(f"  - {msg.sender.username} → {msg.recipient.username}: {msg.message[:50]}...")
        print(f"    Read: {msg.read}, Time: {msg.timestamp}")
    
    # Walk Chat Messages
    print(f"\n🚶 WALK CHAT MESSAGES ({WalkChatMessage.objects.count()} total):")
    walk_messages = WalkChatMessage.objects.all()[:5]  # Show first 5
    for msg in walk_messages:
        print(f"  - {msg.user.username} in '{msg.walk.title}': {msg.message[:50]}...")
    
    # Ad Campaigns (if they exist)
    try:
        campaigns = AdCampaign.objects.all()
        print(f"\n📢 AD CAMPAIGNS ({campaigns.count()} total):")
        for campaign in campaigns:
            print(f"  - {campaign.name}: {campaign.description[:50]}...")
            print(f"    Active: {campaign.is_active}, Budget: ${campaign.budget}")
    except Exception as e:
        print(f"\n📢 AD CAMPAIGNS: Table doesn't exist yet - {e}")
    
    # Ad Events (if they exist)
    try:
        events = AdEvent.objects.all()
        print(f"\n📊 AD EVENTS ({events.count()} total):")
        for event in events[:5]:  # Show first 5
            print(f"  - {event.event_type} on {event.placement} by {event.user.username if event.user else 'Anonymous'}")
            print(f"    Revenue: ${event.revenue}, Time: {event.created_at}")
    except Exception as e:
        print(f"\n📊 AD EVENTS: Table doesn't exist yet - {e}")
    
    print("\n" + "=" * 50)
    print("✅ Database data viewing complete!")

if __name__ == '__main__':
    view_database_data() 