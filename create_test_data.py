#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_walking_buddy.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import User, Profile, Friendship
from chat.models import DirectMessage
from walks.models import Walk, WalkParticipant, WalkChatMessage
from ads.models import AdEvent, AdCampaign
from datetime import datetime, timedelta
import random

User = get_user_model()

def create_test_data():
    print("🚀 Creating test data...")
    
    # Create superuser if it doesn't exist
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        print(f"✅ Created superuser: {admin.username}")
    else:
        admin = User.objects.get(username='admin')
        print(f"✅ Using existing superuser: {admin.username}")
    
    # Create test users
    test_users = []
    for i in range(5):
        username = f'testuser{i+1}'
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f'{username}@test.com',
                password='test123',
                first_name=f'Test{i+1}',
                last_name='User',
                is_online=random.choice([True, False])
            )
            test_users.append(user)
            print(f"✅ Created user: {user.username}")
        else:
            user = User.objects.get(username=username)
            test_users.append(user)
            print(f"✅ Using existing user: {user.username}")
    
    # Create some test walks
    walks = []
    for i in range(3):
        walk = Walk.objects.create(
            title=f'Test Walk {i+1}',
            description=f'This is a test walk #{i+1}',
            start_latitude=40.7128 + random.uniform(-0.1, 0.1),
            start_longitude=-74.0060 + random.uniform(-0.1, 0.1),
            distance=random.uniform(1.0, 5.0),
            duration=random.randint(30, 120),
            start_time=datetime.now() + timedelta(hours=i+1),
            status='active',
            tags=['nature', 'exercise']
        )
        walks.append(walk)
        print(f"✅ Created walk: {walk.title}")
    
    # Add participants to walks
    for walk in walks:
        participants = random.sample(test_users, min(3, len(test_users)))
        for user in participants:
            WalkParticipant.objects.create(
                walk=walk,
                user=user,
                rating=random.randint(3, 5) if random.choice([True, False]) else None
            )
        print(f"✅ Added {len(participants)} participants to {walk.title}")
    
    # Create some direct messages
    for i in range(10):
        sender = random.choice(test_users)
        receiver = random.choice([u for u in test_users if u != sender])
        
        message = DirectMessage.objects.create(
            sender=sender,
            recipient=receiver,
            message=f'Test message #{i+1} from {sender.username} to {receiver.username}',
            read=random.choice([True, False])
        )
        print(f"✅ Created message: {message.message[:30]}...")
    
    # Create some walk chat messages
    for i in range(5):
        walk = random.choice(walks)
        user = random.choice(test_users)
        
        message = WalkChatMessage.objects.create(
            walk=walk,
            user=user,
            message=f'Walk chat message #{i+1} from {user.username}'
        )
        print(f"✅ Created walk chat message: {message.message[:30]}...")
    
    # Create some ad campaigns
    campaigns = []
    for i in range(2):
        campaign = AdCampaign.objects.create(
            name=f'Test Campaign {i+1}',
            description=f'This is test campaign #{i+1}',
            is_active=True,
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now() + timedelta(days=30),
            budget=random.uniform(100, 1000)
        )
        campaigns.append(campaign)
        print(f"✅ Created ad campaign: {campaign.name}")
    
    # Create some ad events
    for i in range(20):
        user = random.choice(test_users) if random.choice([True, False]) else None
        event_type = random.choice(['impression', 'click'])
        placement = random.choice(['homepage', 'chat', 'profile', 'sidebar'])
        
        ad_event = AdEvent.objects.create(
            user=user,
            event_type=event_type,
            placement=placement,
            ad_id=f'ad_{random.randint(1, 100)}',
            revenue=random.uniform(0.01, 0.50) if event_type == 'click' else 0.0,
            ip_address=f'192.168.1.{random.randint(1, 255)}'
        )
        print(f"✅ Created ad event: {ad_event.event_type} on {ad_event.placement}")
    
    print("\n🎉 Test data creation complete!")
    print(f"📊 Created: {len(test_users)} users, {len(walks)} walks, 10 messages, 5 walk chat messages, 2 ad campaigns, 20 ad events")

if __name__ == '__main__':
    create_test_data() 