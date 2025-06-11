#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_walking_buddy.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import User

User = get_user_model()

def fix_duplicate_users():
    print("🔍 CHECKING FOR DUPLICATE USERS")
    print("=" * 50)
    
    # Find users with duplicate emails
    from django.db.models import Count
    duplicate_emails = User.objects.values('email').annotate(
        count=Count('email')
    ).filter(count__gt=1)
    
    if not duplicate_emails:
        print("✅ No duplicate emails found!")
        return
    
    print(f"❌ Found {len(duplicate_emails)} duplicate email(s):")
    
    for dup in duplicate_emails:
        email = dup['email']
        users = User.objects.filter(email=email).order_by('date_joined')
        
        print(f"\n📧 Email: {email}")
        print(f"   Found {len(users)} users:")
        
        for i, user in enumerate(users):
            print(f"   {i+1}. {user.username} (ID: {user.id}) - Joined: {user.date_joined}")
            if user.is_superuser:
                print(f"      ⭐ Superuser")
            if user.is_staff:
                print(f"      👑 Staff")
        
        # Keep the first user (oldest), delete the rest
        if len(users) > 1:
            print(f"\n🗑️  Deleting duplicate users...")
            for user in users[1:]:  # Keep first, delete rest
                print(f"   Deleting: {user.username} (ID: {user.id})")
                user.delete()
            print(f"   ✅ Kept: {users[0].username} (ID: {users[0].id})")
    
    print("\n" + "=" * 50)
    print("✅ Duplicate user cleanup complete!")

def show_all_users():
    print("\n👥 CURRENT USERS:")
    print("=" * 30)
    users = User.objects.all().order_by('date_joined')
    for user in users:
        print(f"  - {user.username} ({user.email}) - ID: {user.id}")
        if user.is_superuser:
            print(f"    ⭐ Superuser")
        if user.is_staff:
            print(f"    👑 Staff")

if __name__ == '__main__':
    fix_duplicate_users()
    show_all_users() 