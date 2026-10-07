from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import OpportunityUnlock
from .serializers import OpportunityUnlockSerializer
from .engine import OpportunityUnlockEngine


@extend_schema_view(
    list=extend_schema(description="List actionable opportunity unlock recommendations for an MSME"),
    retrieve=extend_schema(description="Retrieve unlock recommendation details"),
)
class OpportunityUnlockViewSet(viewsets.ModelViewSet):
    queryset = OpportunityUnlock.objects.select_related('strategy', 'scheme').all()
    serializer_class = OpportunityUnlockSerializer
    filterset_fields = ['strategy', 'scheme', 'difficulty', 'status']

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark an unlock recommendation as resolved."""
        unlock = self.get_object()
        unlock.status = 'resolved'
        unlock.save()
        return Response(OpportunityUnlockSerializer(unlock).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='evaluate')
    def evaluate(self, request):
        """
        Ad-hoc evaluation of opportunity unlocks given evaluations and business facts.
        Request Body:
        {
          "evaluations": [...],
          "business_facts": {...}
        }
        """
        evaluations = request.data.get('evaluations', [])
        business_facts = request.data.get('business_facts', {})

        engine = OpportunityUnlockEngine()
        unlocks = engine.evaluate_unlocks(
            evaluations=evaluations,
            business_facts=business_facts
        )
        return Response([u.to_dict() for u in unlocks], status=status.HTTP_200_OK)
