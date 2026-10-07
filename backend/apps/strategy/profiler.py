"""
Critical Path Performance Profiler & Latency Benchmark.
Measures DB query counts, per-stage timing, cache hit rates, and graceful degradation
across the complete intelligence flow:
goal submission -> candidate discovery -> evidence retrieval -> eligibility -> strategy response.
"""
import time
from typing import Dict, Any, List
from django.db import connection, reset_queries
from django.test.utils import CaptureQueriesContext

from apps.business_profiles.models import BusinessGoal, BusinessProfile
from apps.strategy.ai_orchestrator import AIOrchestrator
from apps.policies.cache_service import SchemeCacheService
from apps.rag.pipeline import generate_embedding


class CriticalPathProfiler:
    """Diagnostic tool to profile and benchmark the critical path."""

    @classmethod
    def benchmark_pipeline(cls, goal: BusinessGoal, profile: BusinessProfile) -> Dict[str, Any]:
        """
        Runs the full AI Orchestrator while capturing query count and latency breakdown.
        """
        reset_queries()
        start_time = time.perf_counter()

        with CaptureQueriesContext(connection) as queries_context:
            orchestrator = AIOrchestrator()
            result = orchestrator.execute_goal_pipeline(goal=goal, profile=profile)

        total_elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        total_queries = len(queries_context)

        # Categorize queries
        scheme_queries = [q for q in queries_context.captured_queries if 'schemes' in q['sql'].lower()]
        rule_queries = [q for q in queries_context.captured_queries if 'scheme_rules' in q['sql'].lower()]
        strategy_queries = [q for q in queries_context.captured_queries if 'strategies' in q['sql'].lower()]

        # Collect stage durations from trace
        stage_timings = {step.step_name: step.duration_ms for step in result.steps}

        return {
            "status": result.status,
            "total_latency_ms": total_elapsed_ms,
            "total_queries_executed": total_queries,
            "query_breakdown": {
                "scheme_queries": len(scheme_queries),
                "rule_queries": len(rule_queries),
                "strategy_queries": len(strategy_queries),
                "other_queries": total_queries - (len(scheme_queries) + len(rule_queries) + len(strategy_queries)),
            },
            "stage_timings_ms": stage_timings,
            "candidates_evaluated": result.candidate_schemes_count,
            "evaluations_summary": result.evaluations_summary,
            "is_n_plus_one_free": len(rule_queries) <= 2,  # Must be batch/prefetched, never N queries
        }

    @classmethod
    def benchmark_embedding_cache(cls, sample_text: str = "Gujarat MSME capital subsidy 25%") -> Dict[str, Any]:
        """
        Benchmarks cold vs warm embedding generation latency.
        """
        # Cold run
        t0 = time.perf_counter()
        _ = generate_embedding(sample_text)
        cold_latency_ms = round((time.perf_counter() - t0) * 1000, 3)

        # Warm cached run
        t0 = time.perf_counter()
        _ = generate_embedding(sample_text)
        warm_latency_ms = round((time.perf_counter() - t0) * 1000, 3)

        return {
            "cold_latency_ms": cold_latency_ms,
            "warm_cached_latency_ms": warm_latency_ms,
            "speedup_factor": round(cold_latency_ms / max(warm_latency_ms, 0.001), 1),
            "is_sub_millisecond": warm_latency_ms < 1.0,
        }

    @classmethod
    def benchmark_scheme_cache(cls) -> Dict[str, Any]:
        """
        Benchmarks cold vs warm scheme metadata loading.
        """
        SchemeCacheService.invalidate_all()

        # Cold DB fetch
        reset_queries()
        with CaptureQueriesContext(connection) as cold_ctx:
            t0 = time.perf_counter()
            cold_schemes = SchemeCacheService.get_active_schemes()
            cold_time_ms = round((time.perf_counter() - t0) * 1000, 2)
            cold_queries = len(cold_ctx)

        # Warm Cached fetch
        reset_queries()
        with CaptureQueriesContext(connection) as warm_ctx:
            t0 = time.perf_counter()
            warm_schemes = SchemeCacheService.get_active_schemes()
            warm_time_ms = round((time.perf_counter() - t0) * 1000, 2)
            warm_queries = len(warm_ctx)

        return {
            "cold_schemes_count": len(cold_schemes),
            "cold_queries": cold_queries,
            "cold_time_ms": cold_time_ms,
            "warm_schemes_count": len(warm_schemes),
            "warm_queries": warm_queries,
            "warm_time_ms": warm_time_ms,
            "zero_query_on_cached": warm_queries == 0,
        }
