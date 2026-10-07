"""
Admin interfaces for curating schemes, policy versions, rules, and document chunks.
"""
from django.contrib import admin
from .models import Scheme, SchemeVersion, SchemeRule, SchemeBenefit, DocumentChunk


class SchemeVersionInline(admin.TabularInline):
    model = SchemeVersion
    extra = 0
    fields = ['version_number', 'change_summary', 'effective_date', 'source_document']
    ordering = ['-version_number']


class SchemeRuleInline(admin.StackedInline):
    model = SchemeRule
    extra = 1
    fields = [
        ('rule_name', 'field_path'),
        ('operator', 'expected_value', 'importance'),
        ('source_clause', 'source_document', 'source_page'),
        ('display_label', 'failure_message'),
        ('order', 'is_active'),
    ]


class SchemeBenefitInline(admin.TabularInline):
    model = SchemeBenefit
    extra = 0
    fields = ['benefit_name', 'benefit_type', 'amount_or_percentage', 'cap_amount_lakhs', 'source_clause']


class DocumentChunkInline(admin.TabularInline):
    model = DocumentChunk
    extra = 0
    fields = ['clause_reference', 'document_title', 'chunk_text', 'effective_date']
    readonly_fields = ['clause_reference', 'document_title', 'effective_date']


@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = [
        'scheme_code', 'name', 'level', 'support_type',
        'status', 'max_benefit_amount_lakhs', 'benefit_percentage',
        'launch_date', 'valid_until'
    ]
    list_filter = ['level', 'support_type', 'status', 'launch_date']
    search_fields = ['scheme_code', 'name', 'short_name', 'ministry_department', 'description']
    inlines = [SchemeVersionInline, SchemeRuleInline, SchemeBenefitInline, DocumentChunkInline]
    fieldsets = (
        ('Scheme Identification', {
            'fields': (
                ('scheme_code', 'name', 'short_name'),
                ('ministry_department', 'implementing_agency'),
                ('level', 'support_type', 'status'),
            )
        }),
        ('Targeting & Scope', {
            'fields': (
                'target_msme_categories',
                'target_sectors',
                'target_states',
            )
        }),
        ('Financial Assistance Details', {
            'fields': (
                ('max_benefit_amount_lakhs', 'benefit_percentage'),
                'benefit_description',
                ('launch_date', 'valid_until'),
            )
        }),
        ('Official Gazette & Source Provenance', {
            'fields': (
                'official_portal_url',
                'official_document_url',
                'gazette_notification',
            )
        }),
        ('Documentation & Guidance', {
            'fields': (
                'description',
                'eligibility_summary',
                'application_process',
            )
        }),
    )


@admin.register(SchemeRule)
class SchemeRuleAdmin(admin.ModelAdmin):
    list_display = ['scheme', 'rule_name', 'field_path', 'operator', 'importance', 'is_active', 'order']
    list_filter = ['importance', 'operator', 'is_active', 'scheme__level']
    search_fields = ['rule_name', 'field_path', 'source_clause', 'scheme__name', 'scheme__scheme_code']
    ordering = ['scheme', 'order', 'importance']


@admin.register(SchemeVersion)
class SchemeVersionAdmin(admin.ModelAdmin):
    list_display = ['scheme', 'version_number', 'effective_date', 'change_summary', 'source_document', 'created_at']
    list_filter = ['effective_date', 'created_at']
    search_fields = ['scheme__name', 'scheme__scheme_code', 'change_summary', 'source_document']


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ['document_title', 'clause_reference', 'scheme', 'effective_date', 'chunk_index']
    list_filter = ['document_type', 'effective_date', 'scheme']
    search_fields = ['document_title', 'clause_reference', 'chunk_text']
