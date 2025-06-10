# Chat app views - placeholder for future API endpoints 
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import DirectMessage
from .serializers import DirectMessageSerializer
from users.models import User
from django.db import models

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