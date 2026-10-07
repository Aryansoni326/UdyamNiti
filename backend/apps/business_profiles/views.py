import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import BusinessProfile, BusinessGoal
from .serializers import (
    BusinessProfileSerializer, BusinessProfileSummarySerializer,
    BusinessGoalSerializer, GoalInputSerializer
)
from apps.strategy.services import StrategyOrchestrator
from apps.strategy.ai_orchestrator import AIOrchestrator


from apps.accounts.permissions import IsOwnerOrAdmin


class BusinessProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = BusinessProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return BusinessProfile.objects.none()
        if user.is_staff or user.is_superuser:
            return BusinessProfile.objects.all()
        return BusinessProfile.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return BusinessProfileSummarySerializer
        return BusinessProfileSerializer

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get a concise profile summary for display."""
        profile = self.get_object()
        serializer = BusinessProfileSummarySerializer(profile)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='provenance')
    def provenance(self, request, pk=None):
        """
        Returns full profile attributes along with field-level provenance metadata
        (self-declared, document-supported, verified, etc.) and snapshot summary.
        """
        from .services import BusinessProfileService
        profile = self.get_object()
        data = BusinessProfileService.get_profile_with_provenance(profile)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='update-with-provenance')
    def update_with_provenance(self, request, pk=None):
        """
        Updates profile fields, records field-level provenance, logs audit change history,
        detects material facts, captures an immutable snapshot, and triggers selective re-evaluation.
        """
        from .services import BusinessProfileService
        from .serializers import ProfileUpdateInputSerializer, ProfileChangeHistorySerializer, ProfileSnapshotSerializer

        profile = self.get_object()
        serializer = ProfileUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        prov_updates = validated.get('field_provenances')
        reason = validated.get('change_reason', 'User profile update')
        trigger_reeval = validated.get('trigger_reevaluation', True)

        # Separate profile fields from meta arguments
        profile_fields = {
            k: v for k, v in validated.items()
            if k not in ('field_provenances', 'change_reason', 'trigger_reevaluation')
        }

        updated_profile, changes, has_material, snapshot = BusinessProfileService.update_profile(
            profile=profile,
            validated_data=profile_fields,
            provenance_updates=prov_updates,
            user=request.user,
            change_reason=reason,
            trigger_reeval=trigger_reeval
        )

        return Response({
            "status": "success",
            "profile_id": str(updated_profile.id),
            "has_material_changes": has_material,
            "reevaluation_triggered": has_material and trigger_reeval,
            "changes_logged": ProfileChangeHistorySerializer(changes, many=True).data,
            "new_snapshot": ProfileSnapshotSerializer(snapshot).data if snapshot else None,
            "current_provenance_summary": BusinessProfileService.get_profile_with_provenance(updated_profile)
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='snapshots')
    def snapshots(self, request, pk=None):
        """Returns the list of frozen immutable profile snapshots for reproducible evaluations."""
        from .serializers import ProfileSnapshotSerializer
        profile = self.get_object()
        snapshots = profile.snapshots.all()
        return Response({
            "profile_id": str(profile.id),
            "count": snapshots.count(),
            "snapshots": ProfileSnapshotSerializer(snapshots, many=True).data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='change-history')
    def change_history(self, request, pk=None):
        """Returns the chronological audit trail of profile modifications."""
        from .serializers import ProfileChangeHistorySerializer
        profile = self.get_object()
        history = profile.change_history.all()
        return Response({
            "profile_id": str(profile.id),
            "count": history.count(),
            "changes": ProfileChangeHistorySerializer(history, many=True).data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='targeted-questions')
    def targeted_questions(self, request, pk=None):
        """
        Returns high-impact clarifying questions targeting missing or self-declared facts
        critical for central + Gujarat schemes, avoiding unnecessary sensitive data.
        """
        from .services import BusinessProfileService
        profile = self.get_object()
        questions = BusinessProfileService.get_targeted_clarifying_questions(profile)
        return Response({
            "profile_id": str(profile.id),
            "questions_count": len(questions),
            "questions": questions
        }, status=status.HTTP_200_OK)



class BusinessGoalViewSet(viewsets.ModelViewSet):
    queryset = BusinessGoal.objects.select_related('business_profile').all()
    serializer_class = BusinessGoalSerializer

    @action(detail=False, methods=['post'])
    def submit(self, request):
        """
        Submit a new business goal for analysis.
        Triggers the full strategy pipeline.
        """
        serializer = GoalInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            profile = BusinessProfile.objects.get(
                pk=serializer.validated_data['business_profile_id']
            )
        except BusinessProfile.DoesNotExist:
            return Response(
                {'error': 'Business profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        goal = BusinessGoal.objects.create(
            business_profile=profile,
            raw_goal_text=serializer.validated_data['goal_text'],
            status='analyzing'
        )

        # Run AI Orchestrator pipeline with correlation ID propagation
        trace_id = (
            request.META.get('HTTP_X_CORRELATION_ID') or
            request.META.get('HTTP_X_TRACE_ID') or
            getattr(request, 'trace_id', None) or
            getattr(request, 'correlation_id', None) or
            f"trace_{uuid.uuid4().hex[:12]}"
        )

        orchestrator = AIOrchestrator()
        result = orchestrator.execute_goal_pipeline(goal=goal, profile=profile, trace_id=trace_id)

        goal.refresh_from_db()
        response_data = {
            'goal': BusinessGoalSerializer(goal).data,
            'strategy_id': result.strategy_id,
            'correlation_id': result.trace_id,
            'trace_id': result.trace_id,
            'status': result.status,
            'steps': [
                {
                    'step_name': s.step_name,
                    'component': s.component,
                    'status': s.status,
                    'duration_ms': s.duration_ms,
                    'output_summary': s.output_summary,
                    'trace_id': s.trace_id
                } for s in result.steps
            ],
            'evaluations_summary': result.evaluations_summary,
            'clarifying_questions': result.clarifying_questions,
            'total_duration_ms': result.total_duration_ms,
        }
        res = Response(
            response_data,
            status=status.HTTP_201_CREATED if result.status != 'FAILED' else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        res['X-Correlation-ID'] = result.trace_id
        res['X-Trace-ID'] = result.trace_id
        return res

    @action(detail=False, methods=['post'], url_path='interpret')
    def interpret(self, request):
        """
        Interprets natural language goal statement in English or Gujarati / Gujlish.
        Returns structured project, investment, categories, and high-impact clarifying questions.
        Strictly NO scheme recommendations are returned at this stage.
        """
        from .goal_agent import GoalUnderstandingAgent
        goal_text = request.data.get('goal_text', '').strip()
        if not goal_text:
            return Response({'error': 'goal_text is required'}, status=status.HTTP_400_BAD_REQUEST)

        profile_id = request.data.get('business_profile_id')
        profile_facts = {}
        if profile_id:
            try:
                profile = BusinessProfile.objects.get(pk=profile_id)
                profile_facts = {
                    'state': profile.state,
                    'district': profile.district,
                    'category': profile.msme_category,
                    'is_manufacturing': profile.is_manufacturing
                }
            except BusinessProfile.DoesNotExist:
                pass

        agent = GoalUnderstandingAgent()
        result = agent.interpret_goal(goal_text, profile_facts)
        return Response(result.to_dict(), status=status.HTTP_200_OK)
