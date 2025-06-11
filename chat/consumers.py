import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import DirectMessage, ChatSession
from users.models import User
from django.utils import timezone
import asyncio


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join user's personal room
        self.room_name = f"user_{self.user.id}"
        self.room_group_name = f"chat_{self.room_name}"
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Update user online status
        await self.update_user_status(True)
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'user_id': self.user.id,
            'username': self.user.username
        }))
    
    async def disconnect(self, close_code):
        # Update user offline status
        await self.update_user_status(False)
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'typing':
            await self.handle_typing(data)
        elif message_type == 'session_keepalive':
            await self.handle_keepalive(data)
        elif message_type == 'mark_read':
            await self.handle_mark_read(data)
    
    async def handle_chat_message(self, data):
        recipient_id = data.get('recipient_id')
        message_text = data.get('message')
        
        if not recipient_id or not message_text:
            return
        
        # Save message to database and create/update session
        message = await self.save_message_and_session(recipient_id, message_text)
        
        if message:
            # Send message to recipient
            recipient_room = f"chat_user_{recipient_id}"
            await self.channel_layer.group_send(
                recipient_room,
                {
                    'type': 'chat_message',
                    'message': message_text,
                    'sender_id': self.user.id,
                    'sender_username': self.user.username,
                    'timestamp': message.timestamp.isoformat(),
                    'message_id': message.id
                }
            )
            
            # Send confirmation to sender
            await self.send(text_data=json.dumps({
                'type': 'message_sent',
                'message_id': message.id,
                'timestamp': message.timestamp.isoformat()
            }))
    
    async def handle_typing(self, data):
        recipient_id = data.get('recipient_id')
        is_typing = data.get('is_typing')
        
        if recipient_id:
            recipient_room = f"chat_user_{recipient_id}"
            await self.channel_layer.group_send(
                recipient_room,
                {
                    'type': 'user_typing',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'is_typing': is_typing
                }
            )
    
    async def handle_keepalive(self, data):
        """Handle session keepalive to maintain connection"""
        await self.send(text_data=json.dumps({
            'type': 'keepalive_response',
            'timestamp': timezone.now().isoformat()
        }))
    
    async def handle_mark_read(self, data):
        """Mark messages as read"""
        sender_id = data.get('sender_id')
        if sender_id:
            await self.mark_messages_read(sender_id)
    
    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))
    
    async def user_typing(self, event):
        """Send typing indicator to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing']
        }))
    
    @database_sync_to_async
    def save_message_and_session(self, recipient_id, message_text):
        """Save message to database and create/update chat session."""
        try:
            recipient = User.objects.get(id=recipient_id)
            
            # Create or update chat session
            ChatSession.get_or_create_session(self.user, recipient)
            
            # Save message
            message = DirectMessage.objects.create(
                sender=self.user,
                recipient=recipient,
                message=message_text
            )
            return message
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def mark_messages_read(self, sender_id):
        """Mark messages from a specific sender as read."""
        DirectMessage.objects.filter(
            sender_id=sender_id,
            recipient=self.user,
            read=False
        ).update(read=True)
    
    @database_sync_to_async
    def update_user_status(self, is_online):
        """Update user online status."""
        self.user.is_online = is_online
        self.user.last_active = timezone.now()
        self.user.save(update_fields=['is_online', 'last_active']) 