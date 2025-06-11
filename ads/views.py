from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import json
import uuid

from .models import AdEvent, AdCampaign


@csrf_exempt
@require_http_methods(["POST"])
def track_ad_event(request):
    """Track ad impressions and clicks."""
    try:
        data = json.loads(request.body)
        event_type = data.get('event_type')
        placement = data.get('placement')
        ad_id = data.get('ad_id')
        
        if not all([event_type, placement, ad_id]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None
        
        # Create ad event
        ad_event = AdEvent.objects.create(
            user=user,
            event_type=event_type,
            placement=placement,
            ad_id=ad_id,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            revenue=0.01 if event_type == 'click' else 0.001  # Basic revenue model
        )
        
        return JsonResponse({'status': 'success', 'id': ad_event.id})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_ad_content(request):
    """Get ad content for a specific placement."""
    placement = request.GET.get('placement', 'homepage')
    
    # Check if user is premium and can hide ads
    if request.user.is_authenticated and request.user.is_premium:
        return Response({'show_ad': False})
    
    # Sample ad content (in production, this would come from a real ad network)
    ads = {
        'homepage': {
            'id': f'homepage_{uuid.uuid4().hex[:8]}',
            'title': 'Find Your Perfect Walking Buddy!',
            'description': 'Join thousands of walkers in your area',
            'image_url': '/static/images/ad-homepage.jpg',
            'link_url': '/register/',
            'cta': 'Get Started Free'
        },
        'chat': {
            'id': f'chat_{uuid.uuid4().hex[:8]}',
            'title': 'Upgrade to Premium',
            'description': 'Unlimited chats, no ads, extended discovery',
            'image_url': '/static/images/ad-premium.jpg',
            'link_url': '/subscribe/',
            'cta': 'Upgrade Now'
        },
        'profile': {
            'id': f'profile_{uuid.uuid4().hex[:8]}',
            'title': 'Boost Your Profile',
            'description': 'Get more profile views and matches',
            'image_url': '/static/images/ad-profile.jpg',
            'link_url': '/subscribe/',
            'cta': 'Learn More'
        }
    }
    
    ad_content = ads.get(placement, ads['homepage'])
    
    return Response({
        'show_ad': True,
        'ad': ad_content
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def ad_stats(request):
    """Get ad performance statistics (admin only)."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=403)
    
    # Get stats for last 30 days
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    
    impressions = AdEvent.objects.filter(
        event_type='impression',
        created_at__gte=thirty_days_ago
    ).count()
    
    clicks = AdEvent.objects.filter(
        event_type='click',
        created_at__gte=thirty_days_ago
    ).count()
    
    revenue = AdEvent.objects.filter(
        created_at__gte=thirty_days_ago
    ).aggregate(total=models.Sum('revenue'))['total'] or 0
    
    ctr = (clicks / impressions * 100) if impressions > 0 else 0
    
    return Response({
        'impressions': impressions,
        'clicks': clicks,
        'click_through_rate': round(ctr, 2),
        'revenue': float(revenue),
        'period': '30 days'
    }) 