from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from users.models import User as CustomUser
from chat.models import ChatSession, DirectMessage
import random
import string
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create a test user and set up a spoofed chat session'

    def handle(self, *args, **options):
        # Generate unique username
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        username = f'testuser_{random_suffix}'
        email = f'{username}@example.com'
        password = 'testpassword123'
        
        try:
            # Create test user with random bio
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=True,
                first_name='Test',
                last_name='User',
                walking_pace='moderate',
                preferred_distance=5.0,
                latitude=37.7749,  # San Francisco
                longitude=-122.4194,
                bio="I'm a test user who loves walking and chatting. I'll respond with 'foobar' to any message you send me!"
            )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created test user {username}'))
            
            # Create spoofed chat session
            chat_session = ChatSession.objects.create(
                user1=user,
                user2=user,
                is_active=True
            )
            
            # Create spoofed message
            message = DirectMessage.objects.create(
                sender=user,
                recipient=user,
                message="Hi! I'm a test user. I'll respond with 'foobar' to any message you send me. Try sending me a message!",
                timestamp=timezone.now()
            )
            
            self.stdout.write(self.style.SUCCESS('Created spoofed chat session and message'))
            
            # Print login credentials
            self.stdout.write(self.style.SUCCESS('Test user credentials:'))
            self.stdout.write(self.style.SUCCESS(f'Username: {username}'))
            self.stdout.write(self.style.SUCCESS(f'Password: {password}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating test user: {str(e)}'))
