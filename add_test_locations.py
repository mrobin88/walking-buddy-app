#!/usr/bin/env python
import os
import django
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_walking_buddy.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import User

User = get_user_model()

def add_test_locations():
    print("📍 ADDING TEST LOCATIONS")
    print("=" * 50)
    
    # Get existing test users
    test_users = User.objects.filter(username__startswith='testuser')
    
    if not test_users.exists():
        print("❌ No test users found. Run create_test_data.py first.")
        return
    
    # Base location (around NYC)
    base_lat = 40.7128
    base_lon = -74.0060
    
    print(f"📍 Adding locations around NYC ({base_lat}, {base_lon})")
    
    for i, user in enumerate(test_users):
        # Add random offset within ~10km radius
        lat_offset = random.uniform(-0.1, 0.1)  # ~11km radius
        lon_offset = random.uniform(-0.1, 0.1)
        
        lat = base_lat + lat_offset
        lon = base_lon + lon_offset
        
        user.latitude = lat
        user.longitude = lon
        user.is_online = True
        user.save(update_fields=['latitude', 'longitude', 'is_online'])
        
        print(f"✅ {user.username}: ({lat:.6f}, {lon:.6f})")
    
    # Also add location to admin user for testing
    try:
        admin = User.objects.get(username='admin')
        admin.latitude = base_lat + 0.05
        admin.longitude = base_lon + 0.05
        admin.is_online = True
        admin.save(update_fields=['latitude', 'longitude', 'is_online'])
        print(f"✅ {admin.username}: ({admin.latitude:.6f}, {admin.longitude:.6f})")
    except User.DoesNotExist:
        pass
    
    print("\n" + "=" * 50)
    print("✅ Test locations added!")
    print("🌍 Users are now positioned around NYC for testing nearby features")

if __name__ == '__main__':
    add_test_locations() 