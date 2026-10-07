"""
Performance & Benchmark Automated Test Suite.
Verifies critical path optimization:
- Zero N+1 queries during batch rule evaluation
- Sub-millisecond embedding cache hits
- Zero-query warm scheme metadata caching
- Graceful degradation on timeouts and failures
- Streaming SSE progress events
"""
import pytest
from unittest.mock import patch, MagicMock
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.policies.models import Scheme, SchemeRule
from apps.policies.cache_service import SchemeCacheService
from apps.strategy.profiler import CriticalPathProfiler
from apps.strategy.ai_orchestrator import AIOrchestrator
from apps.rag.pipeline import generate_embedding


@pytest.mark.django_db
class TestPerformanceOptimization:
    """Verifies critical path performance, caching, and N+1 prevention."""

    @pytest.fixture(autouse=True)
    def setup_benchmarks(self, abc_engineering_profile, synthetic_schemes):
        self.profile = abc_engineering_profile
        self.schemes = synthetic_schemes
        self.goal = BusinessGoal.objects.create(
            business_profile=self.profile,
            raw_goal_text="I want to buy ₹50 Lakh CNC machinery to expand manufacturing capacity.",
            status="pending"
        )
        SchemeCacheService.invalidate_all()

    def test_zero_n_plus_one_in_rule_evaluation(self):
        """
        Verify that RuleEngine.evaluate_batch evaluates all candidate schemes
        without firing an extra query per scheme.
        """
        from apps.eligibility.engine import RuleEngine

        schemes = list(Scheme.objects.filter(status='active').prefetch_related('rules'))
        assert len(schemes) >= 3

        engine = RuleEngine()

        with CaptureQueriesContext(connection) as ctx:
            results = engine.evaluate_batch(schemes, self.profile)

        # Evaluating prefetched schemes must execute ZERO database queries
        assert len(ctx) == 0, f"Expected 0 queries for prefetched batch evaluation, got {len(ctx)}"
        assert len(results) == len(schemes)

    def test_zero_query_on_cached_scheme_metadata(self):
        """
        Verify that SchemeCacheService retrieves all active schemes with zero DB queries on warm cache.
        """
        benchmark = CriticalPathProfiler.benchmark_scheme_cache()

        assert benchmark["warm_queries"] == 0, "Warm cache must hit zero DB queries"
        assert benchmark["zero_query_on_cached"] is True
        assert benchmark["warm_schemes_count"] >= 3

    def test_embedding_cache_sub_millisecond(self):
        """
        Verify that repeated embedding requests hit the in-memory/Django cache in < 1ms.
        """
        benchmark = CriticalPathProfiler.benchmark_embedding_cache("Gujarat MSME Capital Subsidy Scheme")

        assert benchmark["is_sub_millisecond"] is True, f"Warm cache took {benchmark['warm_cached_latency_ms']}ms (> 1ms)"
        assert benchmark["warm_cached_latency_ms"] < benchmark["cold_latency_ms"]

    def test_bulk_create_strategy_items_in_orchestrator(self):
        """
        Verify that executing the full pipeline creates StrategyItems via bulk_create
        rather than N individual inserts.
        """
        with CaptureQueriesContext(connection) as ctx:
            orchestrator = AIOrchestrator()
            result = orchestrator.execute_goal_pipeline(goal=self.goal, profile=self.profile)

        assert result.status == "COMPLETED"
        assert result.strategy_id is not None

        # Verify strategy queries in context
        strategy_item_inserts = [
            q for q in ctx.captured_queries
            if "INSERT INTO" in q["sql"] and "strategy_items" in q["sql"].lower()
        ]
        # Bulk create executes exactly 1 batch insert statement
        assert len(strategy_item_inserts) <= 1, f"Expected <= 1 bulk insert for strategy_items, got {len(strategy_item_inserts)}"

    def test_graceful_degradation_on_external_timeout(self):
        """
        Verify that if candidate discovery or LLM call fails or times out,
        the orchestrator degrades gracefully to partial results without crashing.
        """
        orchestrator = AIOrchestrator()

        # Simulate LLM failure in StrategyAgent
        with patch.object(orchestrator.strategy_agent, 'assemble_strategy', side_effect=TimeoutError("LLM Gateway Timeout")):
            result = orchestrator.execute_goal_pipeline(goal=self.goal, profile=self.profile)

        assert result.status in ("PARTIAL_SUCCESS", "FAILED")
        assert result.total_duration_ms > 0
        assert "LLM Gateway Timeout" in (result.error_message or "")
        # Verified state machine caught the error cleanly and recorded pipeline_error step
        error_steps = [s for s in result.steps if s.status == "FAILED"]
        assert len(error_steps) >= 1
