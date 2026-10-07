"""
Strategy Orchestrator — coordinates all pipeline stages.

Flow:
1. Goal Agent parses intent
2. Scheme Discovery filters candidates
3. Rule Engine evaluates eligibility
4. Relationship Engine finds connections
5. Opportunity Unlock Engine identifies unlock paths
6. Strategy Agent generates narrative
7. Action Agent produces action plan
"""
import logging
from apps.business_profiles.models import BusinessGoal, BusinessProfile
from apps.policies.models import Scheme
from apps.eligibility.engine import RuleEngine
from .agents import GoalAgent, StrategyAgent
from .models import Strategy, StrategyItem

logger = logging.getLogger(__name__)


class StrategyOrchestrator:
    """Main orchestrator for the UdyamNiti intelligence pipeline."""

    def __init__(self):
        self.goal_agent = GoalAgent()
        self.strategy_agent = StrategyAgent()
        self.rule_engine = RuleEngine()

    def analyze(self, goal: BusinessGoal, profile: BusinessProfile) -> dict:
        """
        Execute the full analysis pipeline for a business goal.
        Returns dict with strategy_id and summary results.
        """
        try:
            # Step 1: Parse goal intent
            logger.info(f"Parsing goal: {goal.id}")
            parsed = self.goal_agent.parse(goal.raw_goal_text)
            
            goal.parsed_objective = parsed.get('objective', '')
            goal.parsed_project_type = parsed.get('project_type', '')
            parsed_amount = parsed.get('investment_amount_lakhs')
            if parsed_amount:
                goal.parsed_investment_amount_lakhs = parsed_amount
            goal.parsed_support_categories = parsed.get('support_categories', [])
            goal.parsed_industry_hints = parsed.get('industry_hints', [])
            goal.parsed_missing_info = parsed.get('missing_high_impact_info', [])
            goal.save()

            # Step 2: Discover relevant schemes
            logger.info(f"Discovering schemes for goal: {goal.id}")
            schemes = self._discover_schemes(profile, parsed)

            # Step 3: Evaluate eligibility
            logger.info(f"Evaluating eligibility for {len(schemes)} schemes")
            from apps.eligibility.models import EligibilityEvaluation
            eligible_schemes_data = []
            
            for scheme in schemes:
                result = self.rule_engine.evaluate(scheme, profile)
                
                eval_obj, _ = EligibilityEvaluation.objects.update_or_create(
                    goal=goal,
                    scheme=scheme,
                    defaults={
                        'business_profile': profile,
                        'overall_status': result.overall_status,
                        'score': result.score,
                        'condition_results': [
                            {
                                'rule_id': c.rule_id,
                                'rule_name': c.rule_name,
                                'status': c.status,
                                'explanation': c.explanation,
                                'importance': c.importance,
                                'source_clause': c.source_clause,
                                'display_label': c.display_label,
                            } for c in result.conditions
                        ],
                        'mandatory_failures': result.mandatory_failures,
                        'missing_info': result.missing_info,
                        'summary_explanation': result.summary_explanation,
                    }
                )
                
                eligible_schemes_data.append({
                    'id': str(scheme.id),
                    'name': scheme.name,
                    'code': scheme.scheme_code,
                    'status': result.overall_status,
                    'score': result.score,
                    'benefit': scheme.benefit_description[:100],
                    'support_type': scheme.support_type,
                    'max_benefit_lakhs': result.max_benefit_lakhs,
                })

            # Step 4: Build relationship graph
            relationships = self._evaluate_relationships(schemes)

            # Step 5: Generate strategy narrative
            logger.info(f"Generating strategy narrative")
            narrative = self.strategy_agent.generate_narrative(
                profile, goal.raw_goal_text, eligible_schemes_data, relationships
            )

            # Step 6: Build action plan
            actions = self._build_action_plan(
                profile, goal, eligible_schemes_data, parsed
            )

            # Step 7: Save strategy atomically and invoke domain services
            from django.db import transaction
            from apps.actions.services import ActionPlanService
            from apps.opportunities.services import OpportunityUnlockService

            with transaction.atomic():
                strategy = Strategy.objects.create(
                    goal=goal,
                    business_profile=profile,
                    narrative=narrative,
                    total_opportunities=len(eligible_schemes_data),
                    matched_count=sum(1 for s in eligible_schemes_data if s['status'] == 'MATCH'),
                    potential_count=sum(1 for s in eligible_schemes_data if s['status'] == 'POTENTIAL_MATCH'),
                    action_plan=actions,
                    scheme_results=eligible_schemes_data,
                    relationships=relationships,
                )

                # Save strategy items with zero N+1 queries
                scheme_map = {str(s.id): s for s in schemes}
                strategy_items = [
                    StrategyItem(
                        strategy=strategy,
                        scheme=scheme_map[s_data['id']],
                        status=s_data['status'],
                        score=s_data['score'],
                        priority=self._compute_priority(s_data),
                    )
                    for s_data in eligible_schemes_data if s_data['id'] in scheme_map
                ]
                StrategyItem.objects.bulk_create(strategy_items)

                # Generate domain ActionTasks and OpportunityUnlocks
                ActionPlanService.generate_tasks_for_strategy(strategy, eligible_schemes_data, relationships)
                OpportunityUnlockService.generate_unlocks_for_strategy(strategy, eligible_schemes_data)

                goal.status = 'ready'
                goal.save()

            return {'strategy_id': str(strategy.id)}

        except Exception as e:
            logger.error(f"Orchestrator error: {e}", exc_info=True)
            goal.status = 'error'
            goal.error_message = str(e)
            goal.save()
            return {'strategy_id': None, 'error': str(e)}

    def _discover_schemes(self, profile: BusinessProfile, parsed: dict) -> list:
        """Filter schemes relevant to this profile and goal."""
        qs = Scheme.objects.filter(status='active')
        
        # Filter by MSME category
        if profile.msme_category:
            qs = qs.filter(
                target_msme_categories__contains=[profile.msme_category]
            ) | qs.filter(target_msme_categories=[])
        
        # Filter by state (include central schemes + state-specific)
        state_qs = qs.filter(target_states=[]) | qs.filter(target_states__contains=[profile.state])
        qs = state_qs
        
        # Limit to top 30 most relevant
        return list(qs.prefetch_related('rules', 'benefits')[:30])

    def _evaluate_relationships(self, schemes: list) -> list:
        """Find relationships between discovered schemes."""
        from apps.relationships.models import SchemeRelationship
        
        scheme_ids = [s.id for s in schemes]
        relationships = SchemeRelationship.objects.filter(
            scheme_a__in=scheme_ids, scheme_b__in=scheme_ids
        ).select_related('scheme_a', 'scheme_b')
        
        return [
            {
                'type': r.relationship_type,
                'scheme_a': r.scheme_a.name,
                'scheme_b': r.scheme_b.name,
                'description': r.description,
            }
            for r in relationships
        ]

    def _build_action_plan(self, profile, goal, schemes, parsed) -> list:
        """Generate concrete action items from eligibility results."""
        actions = []
        
        matched = [s for s in schemes if s['status'] == 'MATCH']
        potential = [s for s in schemes if s['status'] == 'POTENTIAL_MATCH']

        if not profile.udyam_registration_number:
            actions.append({
                'priority': 1,
                'category': 'prerequisite',
                'title': 'Register on Udyam Portal',
                'description': 'Udyam Registration is mandatory for most MSME schemes. It is free and instant.',
                'portal': 'https://udyamregistration.gov.in',
                'estimated_time': '1-2 hours',
                'blocker_for': [s['name'] for s in matched[:3]],
            })

        if matched:
            top = matched[0]
            actions.append({
                'priority': 2,
                'category': 'apply_now',
                'title': f"Apply for {top['name']}",
                'description': f"You meet all eligibility criteria. Maximum benefit: ₹{top.get('max_benefit_lakhs', 'N/A')} lakhs.",
                'portal': '#',
                'estimated_time': '1-2 weeks',
                'blocker_for': [],
            })

        if potential:
            top_potential = potential[0]
            actions.append({
                'priority': 3,
                'category': 'resolve_unknowns',
                'title': f"Complete Profile to Unlock {top_potential['name']}",
                'description': 'Add missing business facts to confirm eligibility for additional schemes.',
                'portal': None,
                'estimated_time': '30 minutes',
                'blocker_for': [s['name'] for s in potential[:3]],
            })

        for missing in parsed.get('missing_high_impact_info', [])[:3]:
            actions.append({
                'priority': 4,
                'category': 'information',
                'title': f"Provide: {missing[:60]}",
                'description': f"This information unlocks more accurate eligibility analysis.",
                'portal': None,
                'estimated_time': '5 minutes',
                'blocker_for': [],
            })

        return sorted(actions, key=lambda x: x['priority'])

    def _compute_priority(self, scheme_data: dict) -> int:
        status_priority = {'MATCH': 1, 'POTENTIAL_MATCH': 2, 'UNKNOWN': 3, 'DOES_NOT_MATCH': 4}
        return status_priority.get(scheme_data['status'], 5)
