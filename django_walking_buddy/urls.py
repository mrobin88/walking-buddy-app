"""
URL configuration for walking_buddy project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('users.urls')),
    # path('api/walks/', include('walks.urls')),  # Removed, file does not exist
    path('api/chat/', include('chat.urls')),
    
    # JWT token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Frontend routes (serve index.html for SPA)
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('chat/', TemplateView.as_view(template_name='chat.html'), name='chat'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 