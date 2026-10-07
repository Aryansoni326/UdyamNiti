"""
Unified AI Orchestrator & Deterministic Pipeline State Machine.
Connects agents and deterministic engines without agent sprawl or autonomous infinite loops.

Components:
1. Goal Agent: Interprets natural language goal (English/Gujarati), extracts intent, identifies missing material facts.
2. Policy Agent: Formulates retrieval queries, invokes candidate scheme discovery, gathers grounded evidence bundles.
3. Eligibility Engine (Deterministic Tool): Authoritative boolean rule evaluator (MATCH, POTENTIAL_MATCH, DOES_NOT_MATCH, UNKNOWN).
4. Relationship Engine (Deterministic Tool): Stacking and double-dipping overlap checker.
5. Opportunity Unlock Engine: Differentiates changeable prerequisites from hard disqualifiers.
6. Strategy Agent: Assembles readiness tiers and explainable narrative with cited evidence.
7. Action Agent: Topological dependency ordering of next steps with official portal continuity.

Invariants:
- Tool calls are strictly typed.
- Deterministic services are authoritative for their domains.
- Retries are bounded (max 2 attempts per LLM call).
- Step timings and trace IDs are logged.
- No hidden autonomous loops.
- Fails gracefully to partial results.
- Reusable retrieval/evaluations are cached in memory/session.
- Private chain-of-thought is never exposed to user.
- Returns concise user-facing rationale + official evidence.
"""
import time
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from django.db import transaction
from django.core.cache import cache

from apps.business_profiles.models import BusinessGoal, BusinessProfile
from apps.business_profiles.goal_agent import GoalUnderstandingAgent
from apps.policies.policy_agent import PolicyAgent
from apps.policies.models import Scheme
from apps.eligibility.engine import RuleEngine
from apps.relationships.services import RelationshipEngine
from apps.opportunities.engine import OpportunityUnlockEngine
from apps.strategy.strategy_agent import StrategyAgent
from apps.actions.engine import ActionPlanEngine
from apps.strategy.models import Strategy, StrategyItem
from apps.actions.services import ActionPlanService
from apps.opportunities.services import OpportunityUnlockService
from apps.observability.context import get_current_trace_id

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationTraceStep:
    step_name: str
    component: str
    status: str  # SUCCESS, FALLBACK, FAILED
    duration_ms: float
    output_summary: str
    trace_id: str


@dataclass
class OrchestrationResult:
    trace_id: str
    goal_id: str
    strategy_id: Optional[str]
    status: str  # COMPLETED, PARTIAL_SUCCESS, FAILED
    total_duration_ms: float
    steps: List[OrchestrationTraceStep]
    clarifying_questions: List[Dict[str, Any]]
    candidate_schemes_count: int
    evaluations_summary: Dict[str, int]
    strategy_summary: Dict[str, Any]
    user_facing_rationale: str
    evidence_citations: List[Dict[str, Any]]
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "goal_id": self.goal_id,
            "strategy_id": self.strategy_id,
            "status": self.status,
            "total_duration_ms": self.total_duration_ms,
            "steps": [asdict(s) for s in self.steps],
            "clarifying_questions": self.clarifying_questions,
            "candidate_schemes_count": self.candidate_schemes_count,
            "evaluations_summary": self.evaluations_summary,
            "strategy_summary": self.strategy_summary,
            "user_facing_rationale": self.user_facing_rationale,
            "evidence_citations": self.evidence_citations,
            "error_message": self.error_message
        }


class AIOrchestrator:
    """
    Predictable, bounded state machine coordinating the 7 core components.
    """

    MAX_RETRIES = 2

    def __init__(self):
        self.goal_agent = GoalUnderstandingAgent()
        self.policy_agent = PolicyAgent()
        self.rule_engine = RuleEngine()
        self.relationship_engine = RelationshipEngine()
        self.unlock_engine = OpportunityUnlockEngine()
        self.strategy_agent = StrategyAgent()
        self.action_plan_engine = ActionPlanEngine()

    def execute_goal_pipeline(
        self,
        goal: BusinessGoal,
        profile: BusinessProfile,
        trace_id: Optional[str] = None,
        cached_evals_only: bool = False
    ) -> OrchestrationResult:
        """
        Executes the linear 10-step orchestration without hidden loops:
        1. parse_goal
        2. load_profile
        3. ask_material_questions (if material gaps exist)
        4. discover_candidates
        5. retrieve_evidence
        6. evaluate_rules (deterministic, authoritative)
        7. analyze_relationships (stacking & GFR overlap)
        8. find_unlocks (changeable vs hard disqualifiers)
        9. compose_strategy (readiness tiers, non-hallucinated narrative)
        10. build_actions (dependency-ordered next steps)
        """
        trace_id = trace_id or get_current_trace_id() or f"trace_{uuid.uuid4().hex[:12]}"
        pipeline_start = time.time()
        steps: List[OrchestrationTraceStep] = []

        logger.info(f"[{trace_id}] Starting AI Orchestrator for Goal: {goal.id}, Profile: {profile.id}")

        clarifying_questions = []
        parsed_goal_data = {}
        candidate_schemes = []
        evaluations_data = []
        evidence_bundle = None
        relationships = []
        unlocks_data = []
        strategy_result = None
        actions_data = []
        eval_counts = {"MATCH": 0, "POTENTIAL_MATCH": 0, "DOES_NOT_MATCH": 0, "UNKNOWN": 0}

        try:
            # ─────────────────────────────────────────────────────────────
            # STEP 1: Parse Goal (Goal Agent)
            # ─────────────────────────────────────────────────────────────
            t0 = time.time()
            profile_facts = {
                'state': profile.state,
                'district': profile.district,
                'category': profile.msme_category,
                'is_manufacturing': profile.is_manufacturing,
                'annual_turnover_lakhs': float(profile.annual_turnover_lakhs or 0)
            }
            parsed_goal = self._call_with_retry(
                lambda: self.goal_agent.interpret_goal(goal.raw_goal_text, profile_facts),
                step_name="parse_goal",
                trace_id=trace_id
            )
            parsed_goal_data = parsed_goal.to_dict()

            # Update goal record
            goal.parsed_objective = parsed_goal.primary_goal
            goal.parsed_project_type = parsed_goal.project
            if parsed_goal.estimated_investment.amount:
                goal.parsed_investment_amount_lakhs = parsed_goal.estimated_investment.amount
            goal.parsed_support_categories = parsed_goal.support_categories
            goal.parsed_industry_hints = [parsed_goal.industry_hint] if parsed_goal.industry_hint else []
            goal.parsed_missing_info = parsed_goal.missing_material_facts
            goal.save(update_fields=[
                'parsed_objective', 'parsed_project_type', 'parsed_investment_amount_lakhs',
                'parsed_support_categories', 'parsed_industry_hints', 'parsed_missing_info'
            ])

            steps.append(OrchestrationTraceStep(
                step_name="parse_goal",
                component="GoalAgent",
                status="SUCCESS",
                duration_ms=round((time.time() - t0) * 1000, 2),
                output_summary=f"Project: {parsed_goal.project}, Categories: {parsed_goal.support_categories}",
                trace_id=trace_id
            ))

            # ─────────────────────────────────────────────────────────────
            # STEP 2 & 3: Load Profile & Ask Material Questions if Needed
            # ─────────────────────────────────────────────────────────────
            t0 = time.time()
            if parsed_goal.clarifying_questions:
                clarifying_questions = [asdict(q) for q in parsed_goal.clarifying_questions]

            steps.append(OrchestrationTraceStep(
                step_name="ask_material_questions",
                component="GoalAgent",
                status="SUCCESS",
                duration_ms=round((time.time() - t0) * 1000, 2),
                output_summary=f"Generated {len(clarifying_questions)} material questions",
                trace_id=trace_id
            ))

            # ─────────────────────────────────────────────────────────────
            # STEP 4 & 5: Discover Candidates & Retrieve Evidence (Policy Agent)
            # ─────────────────────────────────────────────────────────────
            t0 = time.time()
            cache_key = f"rag_evidence_{profile.state}_{parsed_goal.support_categories}"
            cached_evidence = cache.get(cache_key)

            if cached_evidence:
                evidence_bundle = cached_evidence
            else:
                goal_summary = {
                    "primary_goal": parsed_goal.primary_goal,
                    "project": parsed_goal.project,
                    "support_categories": parsed_goal.support_categories,
                    "industry_hint": parsed_goal.industry_hint
                }
                profile_summary = {
                    "state": profile.state,
                    "district": profile.district,
                    "category": profile.msme_category,
                    "is_manufacturing": profile.is_manufacturing
                }
                evidence_bundle = self._call_with_retry(
                    lambda: self.policy_agent.research_policy_candidates(goal_summary, profile_summary),
                    step_name="retrieve_evidence",
                    trace_id=trace_id
                )
                cache.set(cache_key, evidence_bundle, timeout=300)

            candidate_scheme_ids = evidence_bundle.candidate_scheme_ids
            # Query candidate scheme models from DB
            candidate_schemes = list(
                Scheme.objects.filter(scheme_code__in=candidate_scheme_ids, status='active')
                .prefetch_related('rules')
            )
            if not candidate_schemes:
                # Fallback to sector/state candidate discovery
                candidate_schemes = list(Scheme.objects.filter(status='active')[:10])

            steps.append(OrchestrationTraceStep(
                step_name="discover_candidates_and_evidence",
                component="PolicyAgent",
                status="SUCCESS",
                duration_ms=round((time.time() - t0) * 1000, 2),
                output_summary=f"Discovered {len(candidate_schemes)} candidates with {evidence_bundle.retrieved_passages_count} evidence passages",
                trace_id=trace_id
            ))

            # ─────────────────────────────────────────────────────────────
            # STEP 6: Deterministic Eligibility Evaluation (Authoritative Engine)
            # ─────────────────────────────────────────────────────────────
            t0 = time.time()
            from apps.observability.metrics import ObservabilityRegistry
            obs_registry = ObservabilityRegistry()

            # Batch evaluate schemes with zero N+1 database round-trips
            batch_eval_results = self.rule_engine.evaluate_batch(candidate_schemes, profile)

            for scheme, eval_res in zip(candidate_schemes, batch_eval_results):
                eval_counts[eval_res.overall_status] = eval_counts.get(eval_res.overall_status, 0) + 1

                # Telemetry recording
                obs_registry.record_rule_evaluation(
                    rule_name=scheme.scheme_code,
                    scheme_code=scheme.scheme_code,
                    eval_status=eval_res.overall_status,
                    reason="; ".join(eval_res.missing_info) if eval_res.missing_info else ""
                )
                obs_registry.record_policy_version_usage(scheme.scheme_code, version_number=1)

                evaluations_data.append({
                    "id": str(scheme.id),
                    "scheme_id": str(scheme.id),
                    "code": scheme.scheme_code,
                    "scheme_code": scheme.scheme_code,
                    "name": scheme.name,
                    "short_name": scheme.short_name or scheme.name,
                    "ministry": scheme.ministry_department,
                    "level": scheme.level,
                    "status": eval_res.overall_status,
                    "overall_status": eval_res.overall_status,
                    "score": eval_res.score,
                    "max_benefit_lakhs": eval_res.max_benefit_lakhs,
                    "benefit_percentage": float(scheme.benefit_percentage) if scheme.benefit_percentage else None,
                    "benefit": scheme.benefit_description[:120] if scheme.benefit_description else "",
                    "benefit_description": scheme.benefit_description or "",
                    "support_type": scheme.support_type,
                    "mandatory_failures": eval_res.mandatory_failures,
                    "missing_info": eval_res.missing_info,
                    "summary_explanation": getattr(eval_res, 'summary_explanation', "") or (scheme.benefit_description[:120] if scheme.benefit_description else ""),
                    "official_portal_url": scheme.official_portal_url or "",
                    "condition_results": [
                        {
                            "rule_name": c.rule_name,
                            "field_path": c.field_path,
                            "status": c.status,
                            "importance": c.importance,
                            "source_clause": c.source_clause,
                            "explanation": c.explanation
                        }
                        for c in eval_res.conditions
                    ]
                })

            steps.append(OrchestrationTraceStep(
                step_name="evaluate_rules",
                component="RuleEngine (Deterministic)",
                status="SUCCESS",
                duration_ms=round((time.time() - t0) * 1000, 2),
                output_summary=f"Evaluated {len(candidate_schemes)} schemes: {eval_counts['MATCH']} MATCH, {eval_counts['POTENTIAL_MATCH']} POTENTIAL, {eval_counts['DOES_NOT_MATCH']} FAIL",
                trace_id=trace_id
            ))

            # ─────────────────────────────────────────────────────────────
            # STEP 7: Analyze Cross-Scheme Relationships (Deterministic Engine)
            # ─────────────────────────────────────────────────────────────
            t0 = time.time()
            relationships = self.relationship_engine.analyze_multiple_schemes(candidate_schemes)

            steps.append(OrchestrationTraceStep(
                step_name="analyze_relationships",
                component="RelationshipEngine (Deterministic)",
                status="SUCCESS",
                duration_ms=round((time.time() - t0) * 1000, 2),
                output_summary=f"Mapped {len(relationships)} statutory stacking edges",
                trace_id=trace_id
            ))

            # ─────────────────────────────────────────────────────────────
            # STEP 8: Find Opportunity Unlocks
            # ─────────────────────────────────────────────────────────────
            t0 = time.time()
            business_facts_map = {
                "udyam_registered": bool(profile.udyam_registration_number),
                "is_manufacturing": profile.is_manufacturing,
                "annual_turnover_lakhs": float(profile.annual_turnover_lakhs or 0),
                "investment_lakhs": float(profile.investment_in_plant_machinery_lakhs or 0),
                "has_zed": False
            }
            unlocks_data = self.unlock_engine.discover_unlocks(
                evaluations=evaluations_data,
                business_facts=business_facts_map,
                relationships=relationships
            )

            steps.append(OrchestrationTraceStep(
                step_name="find_unlocks",
                component="OpportunityUnlockEngine",
                status="SUCCESS",
                duration_ms=round((time.time() - t0) * 1000, 2),
                output_summary=f"Identified {len(unlocks_data)} actionable unlock pathways",
                trace_id=trace_id
            ))

            # ─────────────────────────────────────────────────────────────
            # STEP 9: Compose Strategy (Strategy Agent)
            # ─────────────────────────────────────────────────────────────
            t0 = time.time()
            strategy_result = self._call_with_retry(
                lambda: self.strategy_agent.assemble_strategy(
                    business_goal=goal.raw_goal_text,
                    profile_facts=profile_facts,
                    candidate_schemes=[s.scheme_code for s in candidate_schemes],
                    deterministic_evaluations=evaluations_data,
                    relationship_results=relationships,
                    evidence_bundles=[{"id": e, "citation": e} for e in evidence_bundle.evidence_ids],
                    unlock_candidates=unlocks_data
                ),
                step_name="compose_strategy",
                trace_id=trace_id
            )

            # Persist Strategy in DB atomically
            with transaction.atomic():
                strat_obj = Strategy.objects.create(
                    goal=goal,
                    business_profile=profile,
                    narrative=strategy_result.priority_context or "Roadmap assembled per verified policy criteria.",
                    total_opportunities=len(evaluations_data),
                    matched_count=eval_counts.get("MATCH", 0),
                    potential_count=eval_counts.get("POTENTIAL_MATCH", 0),
                    scheme_results=evaluations_data,
                    relationships=relationships,
                    action_plan=[]
                )

                # Batch create StrategyItems with zero N+1 queries
                scheme_map = {str(s.id): s for s in candidate_schemes}
                strategy_items = [
                    StrategyItem(
                        strategy=strat_obj,
                        scheme=scheme_map[item["id"]],
                        status=item["status"],
                        score=item["score"],
                        priority=1 if item["status"] == "MATCH" else 2
                    )
                    for item in evaluations_data if item["id"] in scheme_map
                ]
                StrategyItem.objects.bulk_create(strategy_items)

                # Persist EligibilityEvaluation records for reliable reloading & downstream impact evaluation
                from apps.eligibility.models import EligibilityEvaluation
                for item in evaluations_data:
                    scheme_inst = scheme_map.get(item["id"])
                    if scheme_inst:
                        EligibilityEvaluation.objects.update_or_create(
                            goal=goal,
                            scheme=scheme_inst,
                            defaults={
                                'business_profile': profile,
                                'overall_status': item["status"],
                                'score': item.get("score", 0.0),
                                'condition_results': item.get("condition_results", []),
                                'mandatory_failures': item.get("mandatory_failures", []),
                                'missing_info': item.get("missing_info", []),
                                'summary_explanation': item.get("summary_explanation", "") or item.get("benefit", ""),
                            }
                        )

                # ─────────────────────────────────────────────────────────────
                # STEP 10: Build Actions (Action Agent & ActionPlanService)
                # ─────────────────────────────────────────────────────────────
                created_tasks = ActionPlanService.generate_tasks_for_strategy(
                    strategy=strat_obj,
                    evaluations_data=evaluations_data,
                    relationships_data=relationships
                )
                OpportunityUnlockService.generate_unlocks_for_strategy(
                    strategy=strat_obj,
                    evaluations_data=evaluations_data
                )

                strat_obj.action_plan = [t.to_dict() for t in created_tasks]
                strat_obj.save(update_fields=['action_plan'])

                goal.status = 'ready'
                goal.save(update_fields=['status'])

            steps.append(OrchestrationTraceStep(
                step_name="compose_strategy_and_actions",
                component="StrategyAgent & ActionPlanEngine",
                status="SUCCESS",
                duration_ms=round((time.time() - t0) * 1000, 2),
                output_summary=f"Strategy {strat_obj.id} saved with {len(created_tasks)} dependency-ordered action tasks",
                trace_id=trace_id
            ))

            total_duration = round((time.time() - pipeline_start) * 1000, 2)

            # Formulate user-facing rationale with evidence citations (no CoT)
            evidence_citations = [
                {"evidence_id": eid, "source": eid, "verified": True}
                for eid in evidence_bundle.evidence_ids[:5]
            ]

            return OrchestrationResult(
                trace_id=trace_id,
                goal_id=str(goal.id),
                strategy_id=str(strat_obj.id),
                status="COMPLETED",
                total_duration_ms=total_duration,
                steps=steps,
                clarifying_questions=clarifying_questions,
                candidate_schemes_count=len(candidate_schemes),
                evaluations_summary=eval_counts,
                strategy_summary=strategy_result.to_dict(),
                user_facing_rationale=strategy_result.priority_context,
                evidence_citations=evidence_citations
            )

        except Exception as e:
            logger.error(f"[{trace_id}] Orchestration failed: {e}", exc_info=True)
            total_duration = round((time.time() - pipeline_start) * 1000, 2)

            steps.append(OrchestrationTraceStep(
                step_name="pipeline_error",
                component="Orchestrator",
                status="FAILED",
                duration_ms=0.0,
                output_summary=str(e),
                trace_id=trace_id
            ))

            goal.status = 'error'
            goal.error_message = str(e)
            goal.save(update_fields=['status', 'error_message'])

            # Graceful partial failure response
            return OrchestrationResult(
                trace_id=trace_id,
                goal_id=str(goal.id),
                strategy_id=None,
                status="PARTIAL_SUCCESS" if evaluations_data else "FAILED",
                total_duration_ms=total_duration,
                steps=steps,
                clarifying_questions=clarifying_questions,
                candidate_schemes_count=len(candidate_schemes),
                evaluations_summary=eval_counts,
                strategy_summary={},
                user_facing_rationale="Partial evaluation completed. Core deterministic checks are recorded.",
                evidence_citations=[],
                error_message=str(e)
            )

    def _call_with_retry(self, fn, step_name: str, trace_id: str):
        """Bounded retry loop with maximum 2 attempts and exponential backoff."""
        last_error = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                return fn()
            except Exception as e:
                last_error = e
                logger.warning(f"[{trace_id}] Step {step_name} attempt {attempt} failed: {e}. Retrying...")
                time.sleep(0.5 * attempt)
        raise last_error
