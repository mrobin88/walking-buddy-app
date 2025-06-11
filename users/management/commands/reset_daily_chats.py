from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import Profile


class Command(BaseCommand):
    help = 'Reset daily chat limits for free users'

    def handle(self, *args, **options):
        # Get all free user profiles
        free_profiles = Profile.objects.filter(is_premium=False)
        
        # Reset daily chat count
        updated_count = free_profiles.update(daily_chats_used=0)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully reset daily chat limits for {updated_count} free users'
            )
        ) 