"""
Django Admin Configuration for Policy Monitoring & Curator Review Workflow.
Provides one-click approval and rejection actions for detected statutory changes.
"""
from django.contrib import admin
from django.utils import timezone
from .models import PolicyChange, ImpactEvaluation, ReviewStatus


@admin.register(PolicyChange)
class PolicyChangeAdmin(admin.ModelAdmin):
    list_display = [
        'scheme',
        'change_type',
        'materiality',
        'review_status',
        'confidence_of_extraction',
        'effective_date',
        'requires_human_review',
        'detected_at'
    ]
    list_filter = [
        'review_status',
        'materiality',
        'requires_human_review',
        'change_type',
        'effective_date'
    ]
    search_fields = [
        'scheme__name',
        'scheme__scheme_code',
        'change_summary',
        'evidence_source'
    ]
    readonly_fields = ['detected_at', 'confidence_of_extraction', 'reviewed_at', 'reviewed_by']
    actions = ['approve_selected_changes', 'reject_selected_changes']

    @admin.action(description="Approve selected changes (Make Active in Rule Engine)")
    def approve_selected_changes(self, request, queryset):
        count = 0
        for change in queryset:
            change.approve(curator_name=request.user.username or "admin_curator")
            count += 1
        self.message_user(request, f"Successfully approved {count} policy changes.")

    @admin.action(description="Reject selected changes")
    def reject_selected_changes(self, request, queryset):
        count = 0
        for change in queryset:
            change.reject(curator_name=request.user.username or "admin_curator")
            count += 1
        self.message_user(request, f"Successfully rejected {count} policy changes.")


@admin.register(ImpactEvaluation)
class ImpactEvaluationAdmin(admin.ModelAdmin):
    list_display = ['business_profile', 'policy_change', 'impact_type', 'notification_sent', 'created_at']
    list_filter = ['notification_sent', 'created_at']
    search_fields = ['business_profile__business_name', 'impact_summary']
