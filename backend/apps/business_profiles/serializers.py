from rest_framework import serializers
from .models import BusinessProfile, BusinessGoal, BusinessFact


class BusinessFactSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessFact
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class BusinessProfileSerializer(serializers.ModelSerializer):
    facts = BusinessFactSerializer(many=True, read_only=True)
    investment_crores = serializers.SerializerMethodField()
    turnover_crores = serializers.SerializerMethodField()

    class Meta:
        model = BusinessProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_investment_crores(self, obj):
        return obj.investment_crores

    def get_turnover_crores(self, obj):
        return obj.turnover_crores


class BusinessProfileSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        fields = [
            'id', 'business_name', 'msme_category', 'entity_type',
            'industry_sector', 'state', 'district',
            'investment_in_plant_machinery_lakhs', 'annual_turnover_lakhs',
            'is_women_owned', 'is_sc_st_owned', 'created_at'
        ]


class BusinessGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessGoal
        fields = '__all__'
        read_only_fields = [
            'id', 'parsed_objective', 'parsed_project_type',
            'parsed_investment_amount_lakhs', 'parsed_support_categories',
            'parsed_industry_hints', 'parsed_missing_info',
            'status', 'error_message', 'created_at', 'updated_at'
        ]


class GoalInputSerializer(serializers.Serializer):
    business_profile_id = serializers.UUIDField()
    goal_text = serializers.CharField(min_length=10, max_length=2000)


class ProfileFieldProvenanceSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import ProfileFieldProvenance
        model = ProfileFieldProvenance
        fields = '__all__'
        read_only_fields = ['id', 'updated_at']


class ProfileChangeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        from .models import ProfileChangeHistory
        model = ProfileChangeHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ProfileSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import ProfileSnapshot
        model = ProfileSnapshot
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ProfileUpdateInputSerializer(serializers.Serializer):
    """
    Typed serializer validating business profile field updates, unit constraints,
    and provenance records.
    """
    # High-value attributes
    state = serializers.CharField(max_length=50, required=False)
    district = serializers.CharField(max_length=100, required=False)
    industry_sector = serializers.CharField(max_length=100, required=False)
    industry_subsector = serializers.CharField(max_length=100, required=False, allow_blank=True)
    msme_category = serializers.ChoiceField(choices=['micro', 'small', 'medium'], required=False)
    entity_type = serializers.CharField(max_length=30, required=False)
    annual_turnover_lakhs = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0, required=False)
    investment_in_plant_machinery_lakhs = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0, required=False)
    total_employees = serializers.IntegerField(min_value=0, required=False)
    udyam_registration_number = serializers.CharField(max_length=50, required=False, allow_blank=True)
    gstin = serializers.CharField(max_length=15, required=False, allow_blank=True)
    has_export_license = serializers.BooleanField(required=False)
    has_iso_certification = serializers.BooleanField(required=False)
    has_bis_certification = serializers.BooleanField(required=False)
    has_gem_registration = serializers.BooleanField(required=False)
    is_manufacturing = serializers.BooleanField(required=False)
    is_service = serializers.BooleanField(required=False)
    is_women_owned = serializers.BooleanField(required=False)
    is_sc_st_owned = serializers.BooleanField(required=False)
    is_npa = serializers.BooleanField(required=False)
    years_in_operation = serializers.IntegerField(min_value=0, required=False)

    # Provenance metadata map: { "field_name": { "source_type": "...", "document_reference": "..." } }
    field_provenances = serializers.DictField(child=serializers.DictField(), required=False)
    change_reason = serializers.CharField(max_length=255, required=False, default="User profile update")
    trigger_reevaluation = serializers.BooleanField(default=True)

