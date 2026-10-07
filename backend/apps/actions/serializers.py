from rest_framework import serializers
from .models import ActionTask


class ActionTaskSerializer(serializers.ModelSerializer):
    category_label = serializers.CharField(source='get_category_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    completion_status = serializers.CharField(read_only=True)

    class Meta:
        model = ActionTask
        fields = [
            'id', 'strategy', 'business_profile', 'scheme',
            'priority', 'title', 'rationale', 'category', 'category_label',
            'description', 'dependency_ids', 'related_scheme_ids', 'evidence_ids',
            'external_url', 'portal_label', 'requires_user_action', 'official_deadline',
            'estimated_time', 'status', 'status_label', 'completion_status',
            'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ApplicationPreparationWorkspaceSerializer(serializers.ModelSerializer):
    scheme_code = serializers.CharField(source='scheme.scheme_code', read_only=True)
    scheme_name = serializers.CharField(source='scheme.name', read_only=True)
    business_name = serializers.CharField(source='business_profile.business_name', read_only=True)

    class Meta:
        from .models import ApplicationPreparationWorkspace
        model = ApplicationPreparationWorkspace
        fields = [
            'id', 'business_profile', 'business_name', 'scheme', 'scheme_code', 'scheme_name',
            'strategy', 'status', 'official_portal_url', 'official_portal_name',
            'application_mode', 'disclaimer_notice', 'workspace_data',
            'documents_ready_count', 'documents_total_count',
            'info_ready_count', 'info_total_count',
            'tasks_completed_count', 'tasks_total_count', 'unknowns_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

