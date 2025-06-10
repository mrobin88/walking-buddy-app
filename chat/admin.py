from django.contrib import admin
from .models import DirectMessage

@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'message', 'read', 'timestamp')
    list_filter = ('read', 'timestamp')
    search_fields = ('sender__username', 'recipient__username', 'message')
    ordering = ('-timestamp',) 