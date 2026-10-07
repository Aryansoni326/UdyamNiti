from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.rag.views import (
    PolicySourceDocumentViewSet,
    PolicyDocumentChunkViewSet,
    IngestionReportViewSet,
    EvidenceSearchAPIView,
    HybridRetrieveAPIView,
    EvaluationBenchmarkAPIView,
    GroundedAnswerComposerAPIView,
    FullRAGEvaluationReportAPIView
)

router = DefaultRouter()
router.register(r'documents', PolicySourceDocumentViewSet, basename='rag-document')
router.register(r'chunks', PolicyDocumentChunkViewSet, basename='rag-chunk')
router.register(r'reports', IngestionReportViewSet, basename='rag-report')

urlpatterns = [
    path('hybrid-retrieve/', HybridRetrieveAPIView.as_view(), name='rag-hybrid-retrieve'),
    path('compose-answer/', GroundedAnswerComposerAPIView.as_view(), name='rag-compose-answer'),
    path('evaluation-benchmark/', EvaluationBenchmarkAPIView.as_view(), name='rag-eval-benchmark'),
    path('evaluation-report/', FullRAGEvaluationReportAPIView.as_view(), name='rag-eval-full-report'),
    path('search/', EvidenceSearchAPIView.as_view(), name='rag-evidence-search'),
    path('', include(router.urls)),
]
