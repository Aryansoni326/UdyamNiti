from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Strategy
from apps.eligibility.models import EligibilityEvaluation
from apps.policies.models import Scheme
from apps.relationships.models import SchemeRelationship


from apps.accounts.permissions import IsOwnerOrAdmin


class StrategyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Strategy.objects.none()
        if user.is_staff or user.is_superuser:
            return Strategy.objects.select_related('goal', 'business_profile').all()
        return Strategy.objects.filter(business_profile__user=user).select_related('goal', 'business_profile')

    def retrieve(self, request, pk=None):
        try:
            strategy = (
                Strategy.objects.select_related('goal', 'business_profile')
                .prefetch_related('unlocks')
                .get(pk=pk)
            )
            self.check_object_permissions(request, strategy)
        except Strategy.DoesNotExist:
            return Response({'error': 'Strategy not found'}, status=404)

        evaluations = EligibilityEvaluation.objects.filter(
            goal=strategy.goal
        ).select_related('scheme').order_by('-score', '-relevance_score')

        schemes_with_details = []
        for ev in evaluations:
            schemes_with_details.append({
                'id': str(ev.scheme.id),
                'scheme_code': ev.scheme.scheme_code,
                'name': ev.scheme.name,
                'short_name': ev.scheme.short_name,
                'ministry': ev.scheme.ministry_department,
                'level': ev.scheme.level,
                'support_type': ev.scheme.support_type,
                'status': ev.overall_status,
                'score': ev.score,
                'max_benefit_lakhs': float(ev.scheme.max_benefit_amount_lakhs) if ev.scheme.max_benefit_amount_lakhs else None,
                'benefit_percentage': float(ev.scheme.benefit_percentage) if ev.scheme.benefit_percentage else None,
                'benefit_description': ev.scheme.benefit_description,
                'description': ev.scheme.description,
                'eligibility_summary': ev.scheme.eligibility_summary,
                'application_process': ev.scheme.application_process,
                'official_portal_url': ev.scheme.official_portal_url,
                'summary_explanation': ev.summary_explanation,
                'mandatory_failures': ev.mandatory_failures,
                'missing_info': ev.missing_info,
                'condition_results': ev.condition_results,
            })

        # Fallback to strategy.scheme_results if evaluations empty in database
        if not schemes_with_details and strategy.scheme_results:
            for item in strategy.scheme_results:
                schemes_with_details.append({
                    'id': str(item.get('id') or item.get('scheme_id')),
                    'scheme_code': item.get('scheme_code') or item.get('code', ''),
                    'name': item.get('name', ''),
                    'short_name': item.get('short_name') or item.get('name', ''),
                    'ministry': item.get('ministry', ''),
                    'level': item.get('level', 'central'),
                    'support_type': item.get('support_type', ''),
                    'status': item.get('status') or item.get('overall_status', 'UNKNOWN'),
                    'score': float(item.get('score', 0.0)),
                    'max_benefit_lakhs': float(item.get('max_benefit_lakhs')) if item.get('max_benefit_lakhs') is not None else None,
                    'benefit_percentage': float(item.get('benefit_percentage')) if item.get('benefit_percentage') is not None else None,
                    'benefit_description': item.get('benefit_description') or item.get('benefit', ''),
                    'description': item.get('description', ''),
                    'eligibility_summary': item.get('eligibility_summary', ''),
                    'application_process': item.get('application_process', ''),
                    'official_portal_url': item.get('official_portal_url', ''),
                    'summary_explanation': item.get('summary_explanation', ''),
                    'mandatory_failures': item.get('mandatory_failures', []),
                    'missing_info': item.get('missing_info', []),
                    'condition_results': item.get('condition_results', []),
                })

        # Relationships
        scheme_ids = [ev.scheme.id for ev in evaluations]
        relationships = SchemeRelationship.objects.filter(
            scheme_a__in=scheme_ids, scheme_b__in=scheme_ids
        ).select_related('scheme_a', 'scheme_b')

        rel_data = [
            {
                'type': r.relationship_type,
                'scheme_a_name': r.scheme_a.name,
                'scheme_a_code': r.scheme_a.scheme_code,
                'scheme_b_name': r.scheme_b.name,
                'scheme_b_code': r.scheme_b.scheme_code,
                'description': r.description,
            }
            for r in relationships
        ]

        if not rel_data and strategy.relationships:
            rel_data = strategy.relationships

        action_plan_data = strategy.action_plan
        if not action_plan_data:
            from apps.actions.models import ActionTask
            tasks = ActionTask.objects.filter(strategy=strategy).order_by('order', 'priority')
            if not tasks.exists():
                tasks = ActionTask.objects.filter(business_profile=strategy.business_profile).order_by('order', 'priority')
            action_plan_data = [t.to_dict() for t in tasks]

        unlocks_data = [
            {
                'id': str(u.id),
                'title': u.title,
                'description': u.description,
                'missing_fact_key': u.missing_fact_key,
                'action_required': u.action_required,
                'potential_benefit_lakhs': float(u.potential_benefit_lakhs) if u.potential_benefit_lakhs else None,
                'difficulty': u.difficulty,
                'estimated_days': u.estimated_days,
                'status': u.status,
            }
            for u in strategy.unlocks.all()
        ]

        trace_id = (
            request.META.get('HTTP_X_CORRELATION_ID') or
            request.META.get('HTTP_X_TRACE_ID') or
            getattr(request, 'trace_id', None) or
            getattr(request, 'correlation_id', None) or
            f"trc_{strategy.id.hex[:12]}"
        )

        response = Response({
            'id': str(strategy.id),
            'correlation_id': trace_id,
            'trace_id': trace_id,
            'goal': {
                'id': str(strategy.goal.id),
                'raw_goal_text': strategy.goal.raw_goal_text,
                'parsed_objective': strategy.goal.parsed_objective,
                'parsed_project_type': strategy.goal.parsed_project_type,
                'parsed_investment_amount_lakhs': float(strategy.goal.parsed_investment_amount_lakhs) if strategy.goal.parsed_investment_amount_lakhs else None,
                'parsed_support_categories': strategy.goal.parsed_support_categories,
                'parsed_missing_info': strategy.goal.parsed_missing_info,
                'status': strategy.goal.status,
            },
            'business_profile': {
                'id': str(strategy.business_profile.id),
                'business_name': strategy.business_profile.business_name,
                'msme_category': strategy.business_profile.msme_category,
                'industry_sector': strategy.business_profile.industry_sector,
                'state': strategy.business_profile.state,
                'district': strategy.business_profile.district,
                'investment_lakhs': float(strategy.business_profile.investment_in_plant_machinery_lakhs) if strategy.business_profile.investment_in_plant_machinery_lakhs else None,
                'turnover_lakhs': float(strategy.business_profile.annual_turnover_lakhs) if strategy.business_profile.annual_turnover_lakhs else None,
                'udyam_number': strategy.business_profile.udyam_registration_number,
                'is_women_owned': strategy.business_profile.is_women_owned,
                'is_sc_st_owned': strategy.business_profile.is_sc_st_owned,
                'is_npa': strategy.business_profile.is_npa,
            },
            'narrative': strategy.narrative,
            'total_opportunities': strategy.total_opportunities,
            'matched_count': strategy.matched_count,
            'potential_count': strategy.potential_count,
            'schemes': schemes_with_details,
            'relationships': rel_data,
            'action_plan': action_plan_data,
            'unlock_recommendations': unlocks_data,
            'created_at': strategy.created_at.isoformat(),
        })
        response['X-Correlation-ID'] = trace_id
        response['X-Trace-ID'] = trace_id
        return response

    @action(detail=False, methods=['get'])
    def for_goal(self, request):
        """Get strategy for a specific goal ID."""
        goal_id = request.query_params.get('goal_id')
        if not goal_id:
            return Response({'error': 'goal_id required'}, status=400)
        try:
            strategy = Strategy.objects.get(goal_id=goal_id)
            return self.retrieve(request, pk=str(strategy.id))
        except Strategy.DoesNotExist:
            return Response({'error': 'No strategy found for this goal'}, status=404)

    @action(detail=False, methods=['post'], url_path='assemble')
    def assemble(self, request):
        """
        Invoke the Strategy Agent to organize deterministic opportunities into a coherent roadmap.
        Accepts:
            - business_goal (dict)
            - profile_snapshot (dict)
            - candidate_scheme_codes (list[str])
            - deterministic_eligibility_results (dict[str, str])
            - relationship_results (list[dict])
            - evidence_bundles (list[dict])
            - unlock_candidates (list[dict])
        Returns validated StrategyAgentOutput schema.
        """
        from .strategy_agent import StrategyAgent

        business_goal = request.data.get('business_goal', {})
        profile_snapshot = request.data.get('profile_snapshot', {})
        scheme_codes = request.data.get('candidate_scheme_codes', [])
        deterministic_results = request.data.get('deterministic_eligibility_results', {})
        relationship_results = request.data.get('relationship_results', [])
        evidence_bundles = request.data.get('evidence_bundles', [])
        unlock_candidates = request.data.get('unlock_candidates', [])

        schemes = list(Scheme.objects.filter(scheme_code__in=scheme_codes))

        agent = StrategyAgent()
        output = agent.organize_strategy(
            business_goal=business_goal,
            profile_snapshot=profile_snapshot,
            candidate_schemes=schemes,
            deterministic_eligibility_results=deterministic_results,
            relationship_results=relationship_results,
            evidence_bundles=evidence_bundles,
            unlock_candidates=unlock_candidates
        )

        return Response(output.to_dict(), status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='why-path')
    def why_path(self, request):
        """
        Reconstruct statutory 'Why?' causal chain for a scheme recommendation:
        Business Fact -> Rule -> Scheme -> Official Evidence -> Result -> Relationship/Blocker -> Action.
        Query params:
          - strategy_id (required)
          - scheme_code (required)
        """
        from .evidence_graph_service import EvidenceGraphService

        strategy_id = request.query_params.get('strategy_id')
        scheme_code = request.query_params.get('scheme_code')

        if not strategy_id or not scheme_code:
            return Response(
                {'error': 'strategy_id and scheme_code query parameters are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = EvidenceGraphService()
        result = service.get_why_path(strategy_id=strategy_id, scheme_code=scheme_code)
        if "error" in result and not result.get("nodes"):
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='evidence-graph')
    def evidence_graph(self, request, pk=None):
        """
        Returns the full Evidence Graph for this strategy recommendation in compact JSON format.
        """
        from .evidence_graph_service import EvidenceGraphService

        service = EvidenceGraphService()
        result = service.get_full_graph(strategy_id=str(pk))
        if "error" in result:
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='orchestrate')
    def orchestrate(self, request):
        """
        Executes the Unified AI Orchestrator across the 10-step linear state machine:
        parse_goal -> load_profile -> ask_material_questions -> discover_candidates
        -> retrieve_evidence -> evaluate_rules -> analyze_relationships -> find_unlocks
        -> compose_strategy -> build_actions.
        Payload: { "goal_id": "...", "profile_id": "..." }
        """
        from .ai_orchestrator import AIOrchestrator
        from apps.business_profiles.models import BusinessGoal, BusinessProfile

        goal_id = request.data.get('goal_id')
        profile_id = request.data.get('profile_id')

        if not goal_id or not profile_id:
            return Response(
                {"error": "goal_id and profile_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            goal = BusinessGoal.objects.get(pk=goal_id)
            profile = BusinessProfile.objects.get(pk=profile_id)
        except (BusinessGoal.DoesNotExist, BusinessProfile.DoesNotExist):
            return Response({"error": "Goal or Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        orchestrator = AIOrchestrator()
        result = orchestrator.execute_goal_pipeline(goal=goal, profile=profile)
        return Response(result.to_dict(), status=status.HTTP_200_OK)

    @action(detail=False, methods=['get', 'post'], url_path='stream-orchestrate')
    def stream_orchestrate(self, request):
        """
        Progressively streams strategy generation status as Server-Sent Events (SSE).
        Emits step completion events, preventing browser timeouts and enabling live UI rendering.
        """
        import json
        from django.http import StreamingHttpResponse
        from .ai_orchestrator import AIOrchestrator
        from apps.business_profiles.models import BusinessGoal, BusinessProfile

        goal_id = request.data.get('goal_id') or request.query_params.get('goal_id')
        profile_id = request.data.get('profile_id') or request.query_params.get('profile_id')

        if not goal_id or not profile_id:
            return Response(
                {"error": "goal_id and profile_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            goal = BusinessGoal.objects.get(pk=goal_id)
            profile = BusinessProfile.objects.get(pk=profile_id)
        except (BusinessGoal.DoesNotExist, BusinessProfile.DoesNotExist):
            return Response({"error": "Goal or Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        def event_stream():
            # Initial SSE handshake
            yield f"event: ping\ndata: {json.dumps({'status': 'connected'})}\n\n"

            orchestrator = AIOrchestrator()
            result = orchestrator.execute_goal_pipeline(goal=goal, profile=profile)

            # Stream each trace step
            for step in result.steps:
                payload = {
                    "step_name": step.step_name,
                    "component": step.component,
                    "status": step.status,
                    "duration_ms": step.duration_ms,
                    "summary": step.output_summary,
                }
                yield f"event: step\ndata: {json.dumps(payload)}\n\n"

            # Stream final completion payload
            final_payload = {
                "status": result.status,
                "strategy_id": result.strategy_id,
                "goal_id": result.goal_id,
                "total_duration_ms": result.total_duration_ms,
                "evaluations_summary": result.evaluations_summary,
                "user_facing_rationale": result.user_facing_rationale,
            }
            yield f"event: complete\ndata: {json.dumps(final_payload)}\n\n"

        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response


