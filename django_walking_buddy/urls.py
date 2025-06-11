"""
URL configuration for walking_buddy project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.models import User
from walks.models import Walk

# Sitemap configuration
sitemaps = {
    'users': GenericSitemap({
        'queryset': User.objects.filter(is_active=True),
        'date_field': 'date_joined',
    }, priority=0.6),
    'walks': GenericSitemap({
        'queryset': Walk.objects.all(),
        'date_field': 'created_at',
    }, priority=0.8),
}

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('users.urls')),
    path('api/chat/', include('chat.urls')),
    # path('api/walks/', include('walks.urls')),  # Commented out - file doesn't exist yet
    
    # JWT token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Frontend routes (serve index.html for SPA)
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('chat/', TemplateView.as_view(template_name='chat.html'), name='chat'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
    
    # Stripe endpoints
    path('api/subscribe/', include('users.stripe_urls')),
    path('api/webhook/stripe/', include('users.webhook_urls')),
    
    # Ad endpoints
    path('api/ads/', include('ads.urls')),
    
    # SEO and static pages
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    
    # Static pages
    path('about/', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    path('privacy/', TemplateView.as_view(template_name='pages/privacy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
    path('help/', TemplateView.as_view(template_name='pages/help.html'), name='help'),
    path('contact/', TemplateView.as_view(template_name='pages/contact.html'), name='contact'),
    path('careers/', TemplateView.as_view(template_name='pages/careers.html'), name='careers'),
    path('blog/', TemplateView.as_view(template_name='pages/blog.html'), name='blog'),
    path('press/', TemplateView.as_view(template_name='pages/press.html'), name='press'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 