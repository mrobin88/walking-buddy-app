from django.urls import path
from . import views

urlpatterns = [
    path('track/', views.track_ad_event, name='track_ad_event'),
    path('content/', views.get_ad_content, name='get_ad_content'),
    path('stats/', views.ad_stats, name='ad_stats'),
] 