# Chat app views - placeholder for future API endpoints 
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import DirectMessage
from .serializers import DirectMessageSerializer, UserSearchSerializer
from users.models import User
from django.db import models

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_users(request):
    """
    Search for users based on username, email, or bio.
    Query parameters:
    - query: Search term
    - limit: Optional limit on results (default: 10)
    """
    query = request.query_params.get('query', '')
    limit = int(request.query_params.get('limit', 10))
    
    if not query:
        return Response({'error': 'Search query is required'}, status=400)
    
    # Search across username, email, and bio fields
    users = User.objects.filter(
        models.Q(username__icontains=query) |
        models.Q(email__icontains=query) |
        models.Q(bio__icontains=query)
    ).exclude(id=request.user.id)[:limit]
    
    serializer = UserSearchSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_dm(request, user_id):
    recipient = get_object_or_404(User, pk=user_id)
    message = request.data.get('message', '')
    image = request.FILES.get('image')
    if not message and not image:
        return Response({'error': 'Message or image required'}, status=400)
    dm = DirectMessage.objects.create(
        sender=request.user,
        recipient=recipient,
        message=message,
        image=image
    )
    serializer = DirectMessageSerializer(dm)
    return Response(serializer.data, status=201)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_dms(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)
    dms = DirectMessage.objects.filter(
        (models.Q(sender=request.user, recipient=other_user) |
         models.Q(sender=other_user, recipient=request.user))
    ).order_by('timestamp')
    serializer = DirectMessageSerializer(dms, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_dm_read(request, dm_id):
    dm = get_object_or_404(DirectMessage, pk=dm_id, recipient=request.user)
    dm.read = True
    dm.save(update_fields=['read'])
    return Response({'message': 'Marked as read'})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chat_limits(request):
    """Get user's chat limits and usage."""
    profile = request.user.profile
    return Response({
        'is_premium': profile.is_premium,
        'daily_chats_used': profile.daily_chats_used,
        'daily_chats_limit': 5 if not profile.is_premium else None,
        'can_send_chat': profile.can_send_chat(),
        'remaining_chats': max(0, 5 - profile.daily_chats_used) if not profile.is_premium else None,
    }) 


@login_required
def chat_view(request):
    """Render the main chat interface."""
    return render(request, 'chat.html', {
        'user': request.user,
        'websocket_url': 'wss://' if request.is_secure() else 'ws://' + request.get_host() + '/ws/chat/'
    })