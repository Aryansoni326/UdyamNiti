from django.contrib import admin
from .models import SchemeRelationship


@admin.register(SchemeRelationship)
class SchemeRelationshipAdmin(admin.ModelAdmin):
    list_display = ['scheme_a', 'relationship_type', 'scheme_b', 'confidence']
    list_filter = ['relationship_type']
    search_fields = ['scheme_a__name', 'scheme_b__name', 'description', 'source_evidence']
