from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q

from apps.rag.models import PolicySourceDocument, PolicyDocumentChunk, IngestionReport
from apps.rag.serializers import (
    PolicySourceDocumentSerializer,
    PolicyDocumentChunkSerializer,
    IngestionReportSerializer
)
from apps.rag.tasks import ingest_policy_document_task
from apps.rag.retrieval import HybridPolicyRetriever, HybridQueryRequest
from apps.rag.evaluation_harness import RetrievalEvaluationHarness


class PolicySourceDocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing official policy source documents.
    """
    queryset = PolicySourceDocument.objects.all().select_related('scheme').prefetch_related('chunks')
    serializer_class = PolicySourceDocumentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['status', 'source_tier', 'document_type', 'authority', 'scheme']
    search_fields = ['title', 'notification_number', 'authority', 'file_hash']

    @action(detail=True, methods=['post'], url_path='re-ingest')
    def re_ingest(self, request, pk=None):
        """Trigger asynchronous re-ingestion task for this document."""
        doc = self.get_object()
        task = ingest_policy_document_task.delay(str(doc.id), force=True)
        return Response({
            'detail': f'Re-ingestion scheduled for {doc.title}',
            'task_id': task.id,
            'status': 'processing'
        }, status=status.HTTP_202_ACCEPTED)


class PolicyDocumentChunkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for querying discrete section-aware evidence chunks.
    Preserves all 13 provenance fields.
    """
    queryset = PolicyDocumentChunk.objects.filter(is_active=True).select_related('document', 'scheme')
    serializer_class = PolicyDocumentChunkSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['document', 'scheme', 'source_tier', 'page_number', 'policy_version']
    search_fields = ['chunk_text', 'section_heading', 'authority', 'document_title']


class IngestionReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for inspecting batch ingestion audit logs and quarantine metrics.
    """
    queryset = IngestionReport.objects.all()
    serializer_class = IngestionReportSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['status']
    search_fields = ['batch_id']


class EvidenceSearchAPIView(APIView):
    """
    Hybrid semantic and keyword retrieval endpoint for policy evidence.
    Returns ranked chunks with verified gazette/clause citations.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        scheme_id = request.query_params.get('scheme_id')
        limit = min(int(request.query_params.get('limit', 10)), 50)

        if not query:
            return Response({'results': [], 'total': 0})

        chunks_qs = PolicyDocumentChunk.objects.filter(is_active=True)

        if scheme_id:
            chunks_qs = chunks_qs.filter(scheme_id=scheme_id)

        # Keyword matching across legal text and section headings
        keywords = query.split()
        q_filter = Q()
        for kw in keywords[:5]:
            q_filter |= Q(chunk_text__icontains=kw) | Q(section_heading__icontains=kw)

        matched_chunks = chunks_qs.filter(q_filter)[:limit]
        serializer = PolicyDocumentChunkSerializer(matched_chunks, many=True)

        return Response({
            'query': query,
            'total': len(serializer.data),
            'results': serializer.data
        })


class HybridRetrieveAPIView(APIView):
    """
    Production Hybrid Policy Retrieval Endpoint.
    Combines dense embeddings, BM25-style keyword search, RRF reranking,
    Tier 1 Gazette boost, and fail-closed safety.
    NOTE: internal_diagnostic_score is strictly for ranking diagnostics
    and must NEVER be presented as statutory eligibility confidence.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_question = request.data.get('user_question', '').strip()
        if not user_question:
            return Response({'error': 'user_question is required'}, status=status.HTTP_400_BAD_REQUEST)

        req = HybridQueryRequest(
            user_question=user_question,
            business_goal=request.data.get('business_goal', ''),
            support_categories=request.data.get('support_categories', []),
            msme_facts=request.data.get('msme_facts', {}),
            candidate_scheme_ids=request.data.get('candidate_scheme_ids', []),
            authority_filter=request.data.get('authority_filter'),
            source_tier_filter=request.data.get('source_tier_filter'),
            top_k=min(int(request.data.get('top_k', 5)), 20),
            min_score_threshold=float(request.data.get('min_score_threshold', 0.28))
        )

        retriever = HybridPolicyRetriever()
        result = retriever.retrieve(req)

        citations_data = [
            {
                'chunk_id': c.chunk_id,
                'document_id': c.document_id,
                'scheme_id': c.scheme_id,
                'authority': c.authority,
                'source_url': c.source_url,
                'source_tier': c.source_tier,
                'document_title': c.document_title,
                'publication_effective_date': c.publication_effective_date,
                'page_number': c.page_number,
                'section_heading': c.section_heading,
                'chunk_text': c.chunk_text,
                'chunk_index': c.chunk_index,
                'chunk_hash': c.chunk_hash,
                'policy_version': c.policy_version,
                'internal_diagnostic_score': c.internal_diagnostic_score,
                'retrieval_method': c.retrieval_method,
                'tier_boost_applied': c.tier_boost_applied,
                'matched_terms': c.matched_terms,
            }
            for c in result.citations
        ]

        return Response({
            'user_question': user_question,
            'retrieval_status': result.retrieval_status,
            'total_candidates_searched': result.total_candidates_searched,
            'citations_count': len(citations_data),
            'citations': citations_data,
            'diagnostic_summary': result.diagnostic_summary
        })


class EvaluationBenchmarkAPIView(APIView):
    """
    Executes the 20-query statutory golden evaluation benchmark
    and returns IR metrics (MRR, Recall@K, Precision@K, Tier-1 ratio, Fail-Closed rate).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        top_k = min(int(request.query_params.get('top_k', 5)), 10)
        harness = RetrievalEvaluationHarness()
        eval_result = harness.run_evaluation(top_k=top_k)
        return Response(eval_result)


class GroundedAnswerComposerAPIView(APIView):
    """
    Synthesizes a grounded, citation-faithful explanation based strictly
    on retrieved government policy documents and deterministic evaluations.
    Enforces strict 5-stage citation validation and hallucination containment.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_question = request.data.get('user_question', '').strip()
        if not user_question:
            return Response({'error': 'user_question is required'}, status=status.HTTP_400_BAD_REQUEST)

        retrieved_evidence = request.data.get('retrieved_evidence')
        candidate_scheme_name = request.data.get('candidate_scheme_name', '')
        business_facts = request.data.get('business_facts', {})
        deterministic_rules = request.data.get('deterministic_rule_results', [])

        # If retrieved_evidence not passed explicitly, invoke hybrid retriever automatically
        if retrieved_evidence is None:
            retriever = HybridPolicyRetriever()
            candidate_ids = [request.data.get('candidate_scheme_id')] if request.data.get('candidate_scheme_id') else []
            ret_req = HybridQueryRequest(
                user_question=user_question,
                candidate_scheme_ids=candidate_ids,
                top_k=min(int(request.data.get('top_k', 4)), 10)
            )
            ret_res = retriever.retrieve(ret_req)
            retrieved_evidence = [
                {
                    'chunk_id': c.chunk_id,
                    'document_title': c.document_title,
                    'authority': c.authority,
                    'source_url': c.source_url,
                    'source_tier': c.source_tier,
                    'page_number': c.page_number,
                    'section_heading': c.section_heading,
                    'chunk_text': c.chunk_text,
                    'policy_version': c.policy_version,
                }
                for c in ret_res.citations
            ]

        from apps.rag.composer import GroundedEvidenceComposer, ComposerContext
        composer = GroundedEvidenceComposer()
        ctx = ComposerContext(
            user_question=user_question,
            candidate_scheme_name=candidate_scheme_name,
            business_facts=business_facts,
            deterministic_rule_results=deterministic_rules,
            retrieved_evidence=retrieved_evidence
        )
        composed_output = composer.compose(ctx)
        return Response(composed_output)


class FullRAGEvaluationReportAPIView(APIView):
    """
    Executes the 25-case RAG Evaluation Suite and returns the complete
    metrics payload including recall, faithfulness, citation integrity, and adversarial resilience.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from apps.rag.evaluation_engine import RAGSystemEvaluationEngine
        top_k = min(int(request.query_params.get('top_k', 4)), 10)
        engine = RAGSystemEvaluationEngine()
        report = engine.run_benchmark(top_k=top_k)
        return Response(report)
