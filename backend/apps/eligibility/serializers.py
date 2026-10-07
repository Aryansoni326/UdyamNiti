from rest_framework import serializers


class EvidenceDetailSerializer(serializers.Serializer):
    source_clause = serializers.CharField(allow_blank=True)
    evidence_ids = serializers.ListField(child=serializers.CharField(), default=list)


class ConditionItemSerializer(serializers.Serializer):
    rule_id = serializers.CharField()
    description = serializers.CharField()
    business_value = serializers.JSONField(allow_null=True)
    expected_condition = serializers.CharField()
    result = serializers.ChoiceField(choices=[
        ('SATISFIED', 'Satisfied'),
        ('NOT_SATISFIED', 'Not Satisfied'),
        ('UNKNOWN', 'Unknown'),
        ('REQUIRES_OFFICIAL_VERIFICATION', 'Requires Official Verification')
    ])
    evidence = EvidenceDetailSerializer()


class OfficialVerificationItemSerializer(serializers.Serializer):
    rule_id = serializers.CharField()
    description = serializers.CharField()
    fact_key = serializers.CharField()
    verification_path = serializers.CharField()


class EligibilityResponseSerializer(serializers.Serializer):
    overall_status = serializers.ChoiceField(choices=[
        ('MATCH', 'Match'),
        ('POTENTIAL_MATCH', 'Potential Match'),
        ('UNKNOWN', 'Unknown'),
        ('DOES_NOT_MATCH', 'Does Not Match'),
        ('REQUIRES_OFFICIAL_VERIFICATION', 'Requires Official Verification')
    ])
    scheme_id = serializers.CharField()
    scheme_code = serializers.CharField()
    scheme_name = serializers.CharField()
    conditions = ConditionItemSerializer(many=True)
    missing_information = serializers.ListField(child=serializers.CharField(), default=list)
    official_verification_items = OfficialVerificationItemSerializer(many=True, default=list)
    evaluated_at = serializers.CharField()
    scheme_version = serializers.IntegerField(default=1)
    summary_explanation = serializers.CharField(allow_blank=True)
    blockers = serializers.ListField(child=serializers.CharField(), default=list)


class SingleSchemeEvaluationRequestSerializer(serializers.Serializer):
    profile_id = serializers.UUIDField(required=True)
    scheme_id = serializers.CharField(required=True, help_text="Scheme UUID or scheme_code e.g. GJ-CAPITAL-2025")
    goal_id = serializers.UUIDField(required=False, allow_null=True)
    scheme_version = serializers.IntegerField(required=False, allow_null=True)


class BatchEvaluationRequestSerializer(serializers.Serializer):
    profile_id = serializers.UUIDField(required=True)
    scheme_ids = serializers.ListField(child=serializers.CharField(), min_length=1)
    goal_id = serializers.UUIDField(required=False, allow_null=True)


class ReEvaluationRequestSerializer(serializers.Serializer):
    profile_id = serializers.UUIDField(required=True)
    updated_facts = serializers.DictField(required=False, default=dict)
    goal_id = serializers.UUIDField(required=False, allow_null=True)
