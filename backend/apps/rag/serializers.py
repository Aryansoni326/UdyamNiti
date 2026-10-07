from rest_framework import serializers
from apps.rag.models import PolicySourceDocument, PolicyDocumentChunk, IngestionReport


class PolicyDocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyDocumentChunk
        fields = [
            'id',
            'document_id',
            'scheme_id',
            'authority',
            'source_url',
            'source_tier',
            'document_title',
            'publication_effective_date',
            'policy_version',
            'page_number',
            'section_heading',
            'chunk_index',
            'chunk_text',
            'chunk_hash',
            'token_count',
            'is_active',
            'ingested_at'
        ]


class PolicySourceDocumentSerializer(serializers.ModelSerializer):
    chunks_count = serializers.IntegerField(source='chunks.count', read_only=True)

    class Meta:
        model = PolicySourceDocument
        fields = [
            'id',
            'scheme',
            'title',
            'authority',
            'source_url',
            'source_tier',
            'document_type',
            'notification_number',
            'file_hash',
            'content_simhash',
            'version_number',
            'effective_date',
            'effective_until',
            'status',
            'quarantine_reason',
            'total_pages',
            'total_chunks',
            'chunks_count',
            'ingested_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'file_hash', 'content_simhash', 'version_number', 'total_chunks', 'ingested_at', 'updated_at']


class IngestionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionReport
        fields = [
            'id',
            'batch_id',
            'status',
            'total_sources',
            'processed_sources',
            'quarantined_sources',
            'total_chunks_created',
            'duplicates_detected',
            'duration_seconds',
            'error_log',
            'created_at'
        ]
