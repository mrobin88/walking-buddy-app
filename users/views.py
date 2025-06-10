from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import get_object_or_404
from .models import User, Friendship
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserStatsSerializer, UserLocationSerializer, FriendshipSerializer
)
from django.db import models
import psutil
import os
from django.db import connection
from django.http import JsonResponse
from django.conf import settings


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Register a new user."""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Update user status
        user.is_online = True
        user.save(update_fields=['is_online'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Login user with both session and JWT."""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Create session for traditional auth
        login(request, user)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Update user status
        user.is_online = True
        user.save(update_fields=['is_online'])
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserProfileSerializer(user).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout user."""
    # Update user status
    request.user.is_online = False
    request.user.save(update_fields=['is_online'])
    
    logout(request)
    return Response({'message': 'Logged out successfully'})


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    """Get or update user profile."""
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_profile_picture(request):
    """Upload profile picture."""
    if 'profile_picture' not in request.FILES:
        return Response(
            {'error': 'No profile picture provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    request.user.profile_picture = request.FILES['profile_picture']
    request.user.save(update_fields=['profile_picture'])
    
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def stats(request):
    """Get user statistics."""
    serializer = UserStatsSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_location(request):
    """Update user location."""
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    if latitude is None or longitude is None:
        return Response(
            {'error': 'Latitude and longitude are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return Response(
            {'error': 'Invalid coordinates'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    request.user.update_location(latitude, longitude)
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_auth(request):
    """Check if user is authenticated and return user info."""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_friend_request(request):
    """Send friend request to another user."""
    to_user_id = request.data.get('to_user')
    
    if not to_user_id:
        return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        to_user = User.objects.get(public_id=to_user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if Friendship.objects.filter(from_user=request.user, to_user=to_user).exists():
        return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.user == to_user:
        return Response({'error': 'Cannot send friend request to yourself'}, status=status.HTTP_400_BAD_REQUEST)
    
    Friendship.objects.create(from_user=request.user, to_user=to_user)
    return Response({'message': 'Friend request sent successfully'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_friend_request(request, user_id):
    """Accept a friend request."""
    try:
        friendship = Friendship.objects.get(
            from_user__public_id=user_id, 
            to_user=request.user, 
            accepted=False
        )
    except Friendship.DoesNotExist:
        return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
    
    friendship.accepted = True
    friendship.save()
    return Response({'message': 'Friend request accepted'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_friend_request(request, user_id):
    """Reject a friend request."""
    try:
        friendship = Friendship.objects.get(
            from_user__public_id=user_id, 
            to_user=request.user, 
            accepted=False
        )
    except Friendship.DoesNotExist:
        return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
    
    friendship.delete()
    return Response({'message': 'Friend request rejected'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_friends(request):
    """List user's friends."""
    friendships = Friendship.objects.filter(
        (models.Q(from_user=request.user) | models.Q(to_user=request.user)) & 
        models.Q(accepted=True)
    )
    serializer = FriendshipSerializer(friendships, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_friend_requests(request):
    """List pending friend requests."""
    requests = Friendship.objects.filter(to_user=request.user, accepted=False)
    serializer = FriendshipSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    """Update user profile information."""
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def nearby_users(request):
    """Find users near the current user's location."""
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    radius = float(request.GET.get('radius', 5))  # Default 5km radius
    
    if not lat or not lon:
        return Response(
            {'error': 'Latitude and longitude parameters are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return Response(
            {'error': 'Invalid coordinates'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Simple distance calculation (approximate)
    # In a real app, you'd use PostGIS or similar for accurate geospatial queries
    users = User.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
        is_online=True
    ).exclude(id=request.user.id)
    
    nearby_users = []
    for user in users:
        # Calculate distance using Haversine formula (simplified)
        import math
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = math.radians(lat), math.radians(lon)
        lat2, lon2 = math.radians(float(user.latitude)), math.radians(float(user.longitude))
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = R * c
        
        if distance <= radius:
            user_data = UserProfileSerializer(user).data
            user_data['distance'] = round(distance, 2)
            nearby_users.append(user_data)
    
    # Sort by distance
    nearby_users.sort(key=lambda x: x['distance'])
    return Response(nearby_users)


class UserListView(generics.ListAPIView):
    """List all users (admin only)."""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['is_online', 'walking_pace']
    search_fields = ['username', 'first_name', 'last_name']
    ordering_fields = ['username', 'total_walks', 'average_rating', 'last_active']


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def system_status(request):
    """Get system status and performance metrics."""
    try:
        # System resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database info
        db_size = 0
        if os.path.exists('db.sqlite3'):
            db_size = os.path.getsize('db.sqlite3') / (1024 * 1024)  # MB
        
        # User statistics
        total_users = User.objects.count()
        online_users = User.objects.filter(is_online=True).count()
        
        # Database queries (if DEBUG is True)
        query_count = len(connection.queries) if settings.DEBUG else 0
        
        return JsonResponse({
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2),
            },
            'application': {
                'total_users': total_users,
                'online_users': online_users,
                'database_size_mb': round(db_size, 2),
                'query_count': query_count,
            },
            'status': 'healthy'
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500) 