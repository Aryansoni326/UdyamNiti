from django.contrib import admin
from .models import ActionTask


@admin.register(ActionTask)
class ActionTaskAdmin(admin.ModelAdmin):
    list_display = ['priority', 'title', 'business_profile', 'category', 'status', 'estimated_time', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'description', 'business_profile__business_name']
    ordering = ['priority', 'created_at']
