from rest_framework import serializers
from .models import OpportunityUnlock


class OpportunityUnlockSerializer(serializers.ModelSerializer):
    scheme_name = serializers.CharField(source='scheme.name', read_only=True)
    scheme_code = serializers.CharField(source='scheme.scheme_code', read_only=True)
    difficulty_label = serializers.CharField(source='get_difficulty_display', read_only=True)

    class Meta:
        model = OpportunityUnlock
        fields = [
            'id', 'strategy', 'scheme', 'scheme_name', 'scheme_code',
            'unlock_action', 'current_blocker', 'affected_opportunities',
            'evidence_ids', 'required_user_confirmation', 'explanation',
            'prerequisite_type', 'is_resolvable',
            'title', 'description', 'missing_fact_key', 'action_required',
            'potential_benefit_lakhs', 'difficulty', 'difficulty_label',
            'estimated_days', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
