from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import BusinessDocument
from .serializers import BusinessDocumentSerializer
from .services import DocumentVerificationService


from apps.accounts.permissions import IsOwnerOrAdmin


@extend_schema_view(
    list=extend_schema(description="List enterprise verification documents"),
    retrieve=extend_schema(description="Get details and extracted facts for a document"),
    create=extend_schema(description="Upload a new verification document for an MSME profile"),
)
class BusinessDocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = BusinessDocumentSerializer
    filterset_fields = ['business_profile', 'document_type', 'verification_status']

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return BusinessDocument.objects.none()
        if user.is_staff or user.is_superuser:
            return BusinessDocument.objects.select_related('business_profile').all()
        return BusinessDocument.objects.filter(business_profile__user=user).select_related('business_profile')

    def perform_create(self, serializer):
        doc = serializer.save()
        # Trigger service layer processing
        raw_bytes = None
        if doc.file:
            try:
                raw_bytes = doc.file.read()
            except Exception:
                pass
        DocumentVerificationService.process_uploaded_document(
            document=doc,
            raw_content=raw_bytes,
            performed_by=self.request.user if self.request.user.is_authenticated else None
        )

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Manually trigger fact extraction and generate proposals for a document."""
        document = self.get_object()
        raw_bytes = None
        if document.file:
            try:
                raw_bytes = document.file.read()
            except Exception:
                pass
        result = DocumentVerificationService.process_uploaded_document(
            document=document,
            raw_content=raw_bytes,
            performed_by=request.user if request.user.is_authenticated else None
        )
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='proposals')
    def proposals(self, request, pk=None):
        """
        List extracted fact proposals for this document.
        Shows extracted value vs current self-declared profile value and conflict status.
        """
        from .serializers import DocumentFactProposalSerializer
        document = self.get_object()
        proposals = document.fact_proposals.all()
        return Response({
            "document_id": str(document.id),
            "document_title": document.title,
            "verification_status": document.verification_status,
            "proposals_count": proposals.count(),
            "proposals": DocumentFactProposalSerializer(proposals, many=True).data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='review-proposals')
    def review_proposals(self, request, pk=None):
        """
        User reviews and accepts/rejects candidate extracted facts.
        Accepted facts become document_supported on the profile; rejected facts are discarded.
        Never overwrites profile silently.
        """
        from .serializers import UserReviewDecisionSerializer
        document = self.get_object()
        serializer = UserReviewDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        decisions = serializer.validated_data['decisions']

        result = DocumentVerificationService.apply_user_review_decisions(
            document=document,
            decisions=decisions,
            user=request.user if request.user.is_authenticated else None
        )
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='secure-delete')
    def secure_delete(self, request, pk=None):
        """
        Secure prototype deletion & retention control:
        Purges physical document file and fact extractions, leaving tamper-evident audit log.
        """
        document = self.get_object()
        reason = request.data.get('reason', 'User prototype retention purge')
        result = DocumentVerificationService.delete_document_secure(
            document=document,
            user=request.user if request.user.is_authenticated else None,
            reason=reason
        )
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get', 'post'], url_path='consistency/profile/(?P<profile_id>[^/.]+)')
    def profile_consistency(self, request, profile_id=None):
        """
        Runs comprehensive multi-way consistency check across:
        Business Profile <-> Udyam <-> GST <-> Financial Statement <-> Quotation.
        Detects MATCH, MISSING, CONFLICT, OUTDATED, UNKNOWN.
        Never forces legal correctness; allows facts to remain unresolved.
        """
        from apps.business_profiles.models import BusinessProfile
        from .consistency_engine import DocumentConsistencyEngine
        try:
            profile = BusinessProfile.objects.get(id=profile_id)
        except BusinessProfile.DoesNotExist:
            return Response({"error": "Business profile not found."}, status=status.HTTP_404_NOT_FOUND)

        persist = request.method == 'POST'
        result = DocumentConsistencyEngine.evaluate_profile_consistency(profile, persist=persist)
        return Response(result, status=status.HTTP_200_OK)


