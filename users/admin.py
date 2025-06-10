from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Friendship

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_online', 'total_walks', 'average_rating')
    list_filter = ('is_online', 'walking_pace', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('bio', 'profile_picture', 'walking_pace', 'preferred_distance', 'interests')}),
        ('Statistics', {'fields': ('total_walks', 'total_distance', 'total_time', 'average_rating', 'total_ratings')}),
        ('Location', {'fields': ('latitude', 'longitude')}),
        ('Status', {'fields': ('is_online',)}),
    )
    
    readonly_fields = ('last_active', 'location_updated', 'public_id')

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'accepted', 'created_at')
    list_filter = ('accepted', 'created_at')
    search_fields = ('from_user__username', 'to_user__username')
    ordering = ('-created_at',) 