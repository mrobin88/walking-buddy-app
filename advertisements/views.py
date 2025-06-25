from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Ad
from .serializers import AdSerializer
from users.models import User

# Ad-related views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def nearby_ads(request):
    """Get nearby ads based on user's location."""
    lat = float(request.GET.get('lat', 0))
    lon = float(request.GET.get('lon', 0))
    radius = float(request.GET.get('radius', 50))  # in kilometers
    
    # Get all active ads
    ads = Ad.objects.filter(status='active')
    
    # Calculate distances and sort by proximity
    ads_with_distance = []
    for ad in ads:
        distance = ad.calculate_distance((lat, lon))
        if distance <= radius:
            ads_with_distance.append((ad, distance))
    
    # Sort by distance
    ads_with_distance.sort(key=lambda x: x[1])
    
    # Increment views for each ad
    for ad, _ in ads_with_distance:
        ad.increment_views()
    
    # Serialize and return
    serializer = AdSerializer([ad for ad, _ in ads_with_distance], many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_ad(request):
    """Create a new ad."""
    if not request.user.is_premium:
        return Response({
            'error': 'Premium subscription required to create ads'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = AdSerializer(data=request.data)
    if serializer.is_valid():
        ad = serializer.save(user=request.user)
        
        # Update ad location
        ad.location = {
            'lat': request.user.latitude,
            'lon': request.user.longitude
        }
        ad.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_ads(request):
    """Get all ads belonging to the user."""
    ads = Ad.objects.filter(user=request.user)
    serializer = AdSerializer(ads, many=True)
    return Response(serializer.data)
