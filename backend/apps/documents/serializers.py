from rest_framework import serializers
from .models import BusinessDocument, DocumentAuditLog


class DocumentAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentAuditLog
        fields = ['id', 'action', 'details', 'timestamp']


class BusinessDocumentSerializer(serializers.ModelSerializer):
    audit_logs = DocumentAuditLogSerializer(many=True, read_only=True)
    document_type_label = serializers.CharField(source='get_document_type_display', read_only=True)
    verification_status_label = serializers.CharField(source='get_verification_status_display', read_only=True)

    class Meta:
        model = BusinessDocument
        fields = [
            'id', 'business_profile', 'document_type', 'document_type_label',
            'title', 'file', 'file_hash', 'page_count', 'extraction_method',
            'verification_status', 'verification_status_label',
            'extracted_facts', 'rejection_reason',
            'verified_at', 'created_at', 'updated_at', 'audit_logs'
        ]
        read_only_fields = ['id', 'file_hash', 'page_count', 'extraction_method', 'verification_status', 'verified_at', 'created_at', 'updated_at']


class DocumentFactProposalSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import DocumentFactProposal
        model = DocumentFactProposal
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'reviewed_at']


class ProposalReviewItemSerializer(serializers.Serializer):
    proposal_id = serializers.UUIDField()
    action = serializers.ChoiceField(choices=['accept', 'reject'])


class UserReviewDecisionSerializer(serializers.Serializer):
    decisions = ProposalReviewItemSerializer(many=True)


class CrossDocumentConsistencyReportSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import CrossDocumentConsistencyReport
        model = CrossDocumentConsistencyReport
        fields = '__all__'
        read_only_fields = ['id', 'generated_at']


