#!/usr/bin/env python
"""
Debug script to test JWT token validation
"""
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

def debug_token(token):
    """Debug a JWT token"""
    try:
        # Decode the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        print(f"Token payload: {payload}")
        
        # Get user
        user_id = payload.get('user_id')
        if user_id:
            user = User.objects.get(id=user_id)
            print(f"User found: {user.username} (ID: {user.id})")
            return user
        else:
            print("No user_id in token")
            return None
            
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None
    except User.DoesNotExist:
        print("User not found")
        return None

if __name__ == "__main__":
    # This would be used in Django shell
    pass 