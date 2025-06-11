from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_subscription, name='create_subscription'),
    path('status/', views.subscription_status, name='subscription_status'),
] 