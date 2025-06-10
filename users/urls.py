from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('check-auth/', views.check_auth, name='check_auth'),
    
    # Profile and user data
    path('profile/', views.profile, name='profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('profile/picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('stats/', views.stats, name='stats'),
    path('location/', views.update_location, name='update_location'),
    path('update-location/', views.update_location, name='update_location_new'),
    
    # User discovery
    path('nearby-users/', views.nearby_users, name='nearby_users'),
    
    # Friendship management
    path('friends/send/<uuid:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('send-friend-request/', views.send_friend_request, name='send_friend_request_new'),
    path('friends/accept/<uuid:user_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friends/reject/<uuid:user_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('friends/', views.list_friends, name='list_friends'),
    path('friend-requests/', views.list_friend_requests, name='list_friend_requests'),
    
    # Admin only endpoints
    path('admin/users/', views.UserListView.as_view(), name='user_list'),
    path('system-status/', views.system_status, name='system_status'),
] 