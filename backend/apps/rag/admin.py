from django.contrib import admin
from apps.rag.models import PolicySourceDocument, PolicyDocumentChunk, IngestionReport


class PolicyDocumentChunkInline(admin.TabularInline):
    model = PolicyDocumentChunk
    extra = 0
    fields = ('page_number', 'section_heading', 'token_count', 'is_active', 'chunk_hash')
    readonly_fields = ('chunk_hash', 'token_count')
    can_delete = False
    show_change_link = True


@admin.register(PolicySourceDocument)
class PolicySourceDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'authority', 'source_tier', 'version_number', 'status', 'total_pages', 'total_chunks', 'effective_date')
    list_filter = ('status', 'source_tier', 'document_type', 'authority')
    search_fields = ('title', 'notification_number', 'file_hash', 'authority')
    readonly_fields = ('id', 'file_hash', 'content_simhash', 'version_number', 'total_chunks', 'ingested_at', 'updated_at')
    inlines = [PolicyDocumentChunkInline]


@admin.register(PolicyDocumentChunk)
class PolicyDocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document_title', 'page_number', 'section_heading', 'source_tier', 'policy_version', 'is_active')
    list_filter = ('source_tier', 'is_active', 'policy_version')
    search_fields = ('chunk_text', 'section_heading', 'document_title', 'authority', 'chunk_hash')
    readonly_fields = ('id', 'chunk_hash', 'token_count', 'ingested_at')


@admin.register(IngestionReport)
class IngestionReportAdmin(admin.ModelAdmin):
    list_display = ('batch_id', 'status', 'processed_sources', 'quarantined_sources', 'total_chunks_created', 'duration_seconds', 'created_at')
    list_filter = ('status',)
    search_fields = ('batch_id',)
    readonly_fields = ('id', 'created_at')
