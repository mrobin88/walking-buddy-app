from django.urls import path
from . import views

urlpatterns = [
    path('nearby/', views.nearby_ads, name='nearby_ads'),
    path('create/', views.create_ad, name='create_ad'),
    path('user/', views.user_ads, name='user_ads'),
]
