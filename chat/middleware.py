import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

User = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Get the token from query string or headers
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        
        # Try to get token from query string first
        token = query_params.get('token', [None])[0]
        
        # If not in query string, try to get from headers
        if not token:
            headers = dict(scope['headers'])
            auth_header = headers.get(b'authorization', b'').decode()
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if token:
            try:
                # Decode the JWT token
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                
                if user_id:
                    # Get the user from database
                    user = await self.get_user(user_id)
                    if user:
                        scope['user'] = user
                        return await super().__call__(scope, receive, send)
            except jwt.ExpiredSignatureError:
                pass
            except jwt.InvalidTokenError:
                pass
        
        # If no valid token, set anonymous user
        scope['user'] = await self.get_anonymous_user()
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_anonymous_user(self):
        return User.objects.get_or_create(username='anonymous')[0] 