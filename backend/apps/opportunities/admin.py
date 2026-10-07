from django.contrib import admin
from .models import OpportunityUnlock


@admin.register(OpportunityUnlock)
class OpportunityUnlockAdmin(admin.ModelAdmin):
    list_display = ['title', 'scheme', 'potential_benefit_lakhs', 'difficulty', 'status', 'created_at']
    list_filter = ['status', 'difficulty', 'created_at']
    search_fields = ['title', 'description', 'missing_fact_key']
