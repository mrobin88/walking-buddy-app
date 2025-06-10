from django.urls import path
from . import views

urlpatterns = [
    path('dm/send/<int:user_id>/', views.send_dm, name='send_dm'),
    path('dm/list/<int:user_id>/', views.list_dms, name='list_dms'),
    path('dm/mark-read/<int:dm_id>/', views.mark_dm_read, name='mark_dm_read'),
] 