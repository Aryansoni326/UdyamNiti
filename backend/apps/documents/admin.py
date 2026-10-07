from django.contrib import admin
from .models import BusinessDocument, DocumentAuditLog


class DocumentAuditLogInline(admin.TabularInline):
    model = DocumentAuditLog
    extra = 0
    readonly_fields = ['action', 'details', 'performed_by', 'timestamp']
    can_delete = False


@admin.register(BusinessDocument)
class BusinessDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'business_profile', 'document_type', 'verification_status', 'verified_at', 'created_at']
    list_filter = ['verification_status', 'document_type', 'created_at']
    search_fields = ['title', 'business_profile__business_name', 'file_hash']
    readonly_fields = ['file_hash', 'verified_at', 'created_at', 'updated_at']
    inlines = [DocumentAuditLogInline]
