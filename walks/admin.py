from django.contrib import admin
from .models import Walk, WalkParticipant, WalkPhoto, WalkChatMessage

@admin.register(Walk)
class WalkAdmin(admin.ModelAdmin):
    list_display = ('public_id', 'title', 'status', 'distance', 'duration', 'start_time', 'created_at')
    list_filter = ('status', 'tags', 'start_time', 'created_at')
    search_fields = ('title', 'description', 'participants__user__username')
    ordering = ('-created_at',)
    readonly_fields = ('public_id', 'pace')

@admin.register(WalkParticipant)
class WalkParticipantAdmin(admin.ModelAdmin):
    list_display = ('walk', 'user', 'joined_at', 'left_at', 'rating')
    list_filter = ('joined_at', 'left_at', 'rating')
    search_fields = ('walk__title', 'user__username')

@admin.register(WalkPhoto)
class WalkPhotoAdmin(admin.ModelAdmin):
    list_display = ('walk', 'uploaded_by', 'caption', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('walk__title', 'uploaded_by__username', 'caption')

@admin.register(WalkChatMessage)
class WalkChatMessageAdmin(admin.ModelAdmin):
    list_display = ('walk', 'user', 'message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('walk__title', 'user__username', 'message') 