from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import User as CustomUser
import random

class Command(BaseCommand):
    help = 'Update test user location to a different city'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the test user to update')
        parser.add_argument('--city', type=str, choices=['paris', 'london', 'tokyo', 'sydney', 'oakland'], default='paris',
                          help='City to set the location to')

    def handle(self, *args, **options):
        username = options['username']
        city = options['city']
        
        try:
            user = CustomUser.objects.get(username=username)
            
            # Set location based on chosen city
            if city == 'paris':
                user.latitude = 48.8566  # Paris
                user.longitude = 2.3522
                user.bio = "I'm a test user in Paris. I'll respond with 'foobar' to any message you send me!"
            elif city == 'london':
                user.latitude = 51.5074  # London
                user.longitude = -0.1278
                user.bio = "I'm a test user in London. I'll respond with 'foobar' to any message you send me!"
            elif city == 'tokyo':
                user.latitude = 35.6895  # Tokyo
                user.longitude = 139.6917
                user.bio = "I'm a test user in Tokyo. I'll respond with 'foobar' to any message you send me!"
            elif city == 'sydney':
                user.latitude = -33.8688  # Sydney
                user.longitude = 151.2093
                user.bio = "I'm a test user in Sydney. I'll respond with 'foobar' to any message you send me!"
            elif city == 'Oakland':
                user.latitude = 37.8091 #Oakland 
                user.longitude = -122.2597
                user.bio = "I'm a test user in Oakland. I'll respond with 'foobar' to any message you send me!"
            
            user.save(update_fields=['latitude', 'longitude', 'bio'])
            
            self.stdout.write(self.style.SUCCESS(f'Successfully updated location for user {username}'))
            self.stdout.write(self.style.SUCCESS(f'New location: {city}'))
            self.stdout.write(self.style.SUCCESS(f'Coordinates: {user.latitude}, {user.longitude}'))
            
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating location: {str(e)}'))