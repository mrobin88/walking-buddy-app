from django.urls import path
from . import views

urlpatterns = [
    # Chat page
    path('', views.chat_view, name='chat'),
    
    # API endpoints
    path('dm/search/', views.search_users, name='search_users'),
    path('dm/send/<int:user_id>/', views.send_dm, name='send_dm'),
    path('dm/list/<int:user_id>/', views.list_dms, name='list_dms'),
    path('dm/mark-read/<int:dm_id>/', views.mark_dm_read, name='mark_dm_read'),
    path('dm/limits/', views.chat_limits, name='chat_limits'),
]