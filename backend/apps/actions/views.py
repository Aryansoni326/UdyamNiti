from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import ActionTask
from .serializers import ActionTaskSerializer
from .services import ActionPlanService
from .engine import ActionPlanEngine


from apps.accounts.permissions import IsOwnerOrAdmin


@extend_schema_view(
    list=extend_schema(description="List prioritized action items for an MSME strategy"),
    retrieve=extend_schema(description="Retrieve action item details"),
)
class ActionTaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = ActionTaskSerializer
    filterset_fields = ['strategy', 'business_profile', 'category', 'status']

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return ActionTask.objects.none()
        if user.is_staff or user.is_superuser:
            return ActionTask.objects.select_related('strategy', 'business_profile', 'scheme').all()
        return ActionTask.objects.filter(business_profile__user=user).select_related('strategy', 'business_profile', 'scheme')

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark an action task as completed.
        Validates that all prerequisite tasks in dependency_ids are completed first.
        Optional body parameter: {"force": true} to bypass dependency checks.
        """
        force = request.data.get('force', False)
        try:
            task = ActionPlanService.complete_task(task_id=pk, force=force)
            return Response(ActionTaskSerializer(task).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {"error": str(e), "requires_dependency_completion": True},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Reopen a completed or skipped action task."""
        task = ActionPlanService.reopen_task(task_id=pk)
        return Response(ActionTaskSerializer(task).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        """
        Generate a dependency-aware action plan on the fly.
        Request body:
        {
          "goal": {...},
          "business_facts": {...},
          "selected_opportunities": [...],
          "unknowns": [...]
        }
        """
        goal = request.data.get('goal', {})
        business_facts = request.data.get('business_facts', {})
        selected_opportunities = request.data.get('selected_opportunities', [])
        unknowns = request.data.get('unknowns', [])

        engine = ActionPlanEngine()
        tasks = engine.generate_plan(
            goal=goal,
            business_facts=business_facts,
            selected_opportunities=selected_opportunities,
            unknowns=unknowns
        )
        return Response([t.to_dict() for t in tasks], status=status.HTTP_200_OK)


class ApplicationPreparationWorkspaceViewSet(viewsets.ModelViewSet):
    """
    CRUD and orchestration for the Application Preparation Workspace.
    Prepares documents, form information, condition checklists, and exposes official government route.
    """
    from .models import ApplicationPreparationWorkspace
    from .serializers import ApplicationPreparationWorkspaceSerializer

    permission_classes = [IsOwnerOrAdmin]
    serializer_class = ApplicationPreparationWorkspaceSerializer
    filterset_fields = ['business_profile', 'scheme', 'status']

    def get_queryset(self):
        from .models import ApplicationPreparationWorkspace
        user = self.request.user
        if not user or not user.is_authenticated:
            return ApplicationPreparationWorkspace.objects.none()
        if user.is_staff or user.is_superuser:
            return ApplicationPreparationWorkspace.objects.select_related('business_profile', 'scheme', 'strategy').all()
        return ApplicationPreparationWorkspace.objects.filter(business_profile__user=user).select_related('business_profile', 'scheme', 'strategy')

    @action(detail=False, methods=['post'], url_path='get-or-create')
    def get_or_create(self, request):
        """
        Creates or retrieves an existing preparation workspace for a profile and scheme.
        Payload: { "business_profile_id": "...", "scheme_id": "...", "strategy_id": "..." }
        """
        from .workspace_service import ApplicationWorkspaceService
        from apps.business_profiles.models import BusinessProfile
        profile_id = request.data.get('business_profile_id')
        scheme_id = request.data.get('scheme_id')
        strategy_id = request.data.get('strategy_id')

        if not profile_id or not scheme_id:
            return Response(
                {"error": "business_profile_id and scheme_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Enforce user authorization on profile
        if not (request.user.is_staff or request.user.is_superuser):
            profile = BusinessProfile.objects.filter(id=profile_id, user=request.user).first()
            if not profile:
                return Response(
                    {"error": "Forbidden: You can only create or access workspaces for your own business profile."},
                    status=status.HTTP_403_FORBIDDEN
                )

        workspace = ApplicationWorkspaceService.get_or_create_workspace(
            profile_id=profile_id,
            scheme_id=scheme_id,
            strategy_id=strategy_id
        )
        serializer = self.get_serializer(workspace)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='refresh')
    def refresh(self, request, pk=None):
        """Re-evaluates document availability, info fields, and task progress."""
        from .workspace_service import ApplicationWorkspaceService
        workspace = self.get_object()
        workspace = ApplicationWorkspaceService.refresh_workspace_state(workspace)
        serializer = self.get_serializer(workspace)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='mark-applied')
    def mark_applied(self, request, pk=None):
        """Records that user completed external portal submission."""
        workspace = self.get_object()
        workspace.status = 'applied_external'
        workspace.save(update_fields=['status', 'updated_at'])
        return Response({
            "status": "applied_external",
            "workspace_id": str(workspace.id),
            "message": f"Successfully marked as applied on {workspace.official_portal_name}."
        }, status=status.HTTP_200_OK)

