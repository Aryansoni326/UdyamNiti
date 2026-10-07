"""
Telemetry Metrics Registry for UdyamNiti Modular Monolith.
Tracks and aggregates:
1. API Latencies (p50, p95, p99, avg, max)
2. LLM Call Metrics (Latencies, prompt/completion tokens, model names)
3. Retrieval Performance (Hybrid latency, candidate counts, retrieved evidence IDs)
4. Rule Engine Execution (MATCH, POTENTIAL_MATCH, DOES_NOT_MATCH, UNKNOWN distributions)
5. Fallback & UNKNOWN Frequency (Counts and statutory gap reasons)
6. Background Jobs (Status, durations, success/failure rates)
7. Policy Version Usage (Active versions queried)
8. Recent Request Traces (Ring buffer of last 100 traces for diagnostics dashboard)
"""
import time
import threading
from collections import deque, Counter
from typing import Dict, Any, List, Optional
from datetime import datetime


class ObservabilityRegistry:
    """
    Thread-safe in-memory metrics collector and telemetry aggregator.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_metrics()
            return cls._instance

    def _init_metrics(self):
        self._start_time = time.time()
        self._mutex = threading.Lock()

        # 1. API Request Tracking
        self._total_requests = 0
        self._status_code_counts = Counter()
        self._request_latencies = deque(maxlen=1000)  # rolling window of last 1000 requests
        self._recent_traces = deque(maxlen=100)       # ring buffer of last 100 traces

        # 2. LLM Call Tracking
        self._total_llm_calls = 0
        self._llm_errors = 0
        self._llm_latencies = deque(maxlen=500)
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._llm_models_used = Counter()

        # 3. Retrieval Tracking
        self._total_retrieval_queries = 0
        self._retrieval_latencies = deque(maxlen=500)
        self._retrieved_evidence_ids = Counter()      # Most frequently cited chunks

        # 4. Rule Engine Tracking
        self._total_rule_evaluations = 0
        self._rule_status_distribution = Counter()    # MATCH, POTENTIAL_MATCH, DOES_NOT_MATCH, UNKNOWN
        self._rule_latencies = deque(maxlen=500)

        # 5. Fallback & UNKNOWN Frequency
        self._total_fallbacks = 0
        self._fallback_reasons = Counter()
        self._unknown_rule_reasons = Counter()

        # 6. Background Jobs Tracking
        self._total_background_jobs = 0
        self._job_status_counts = Counter()
        self._job_durations = deque(maxlen=200)

        # 7. Policy Version Usage
        self._policy_versions_used = Counter()        # e.g. "PMEGP:v2", "Atmanirbhar_Gujarat:v1"

    # -------------------------------------------------------------
    # RECORDING METHODS
    # -------------------------------------------------------------

    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        trace_id: str,
        user_id: Optional[str] = None,
        error_summary: Optional[str] = None
    ):
        with self._mutex:
            self._total_requests += 1
            self._status_code_counts[str(status_code)] += 1
            self._request_latencies.append(duration_ms)

            self._recent_traces.appendleft({
                "trace_id": trace_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
                "user_id": user_id or "anonymous",
                "error": error_summary
            })

    def record_llm_call(
        self,
        model_name: str,
        duration_ms: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        success: bool = True,
        fallback_triggered: bool = False
    ):
        with self._mutex:
            self._total_llm_calls += 1
            self._llm_models_used[model_name] += 1
            self._llm_latencies.append(duration_ms)
            self._total_prompt_tokens += prompt_tokens
            self._total_completion_tokens += completion_tokens
            if not success:
                self._llm_errors += 1
            if fallback_triggered:
                self._total_fallbacks += 1
                self._fallback_reasons["llm_generation_offline_or_failed"] += 1

    def record_retrieval(
        self,
        duration_ms: float,
        candidate_count: int,
        evidence_chunk_ids: List[str]
    ):
        with self._mutex:
            self._total_retrieval_queries += 1
            self._retrieval_latencies.append(duration_ms)
            for cid in evidence_chunk_ids:
                self._retrieved_evidence_ids[str(cid)] += 1

    def record_rule_evaluation(
        self,
        rule_name: str,
        scheme_code: str,
        eval_status: str,
        duration_ms: float = 0.0,
        reason: str = ""
    ):
        with self._mutex:
            self._total_rule_evaluations += 1
            self._rule_status_distribution[eval_status] += 1
            if duration_ms > 0:
                self._rule_latencies.append(duration_ms)
            if eval_status == "UNKNOWN" and reason:
                self._unknown_rule_reasons[f"{scheme_code}:{rule_name} - {reason[:60]}"] += 1

    def record_fallback(self, component: str, reason: str, trace_id: Optional[str] = None):
        with self._mutex:
            self._total_fallbacks += 1
            self._fallback_reasons[f"{component}: {reason}"] += 1

    def record_background_job(
        self,
        task_name: str,
        status: str,
        duration_seconds: float,
        error: Optional[str] = None
    ):
        with self._mutex:
            self._total_background_jobs += 1
            self._job_status_counts[status] += 1
            self._job_durations.append(duration_seconds)

    def record_policy_version_usage(self, scheme_code: str, version_number: int):
        with self._mutex:
            self._policy_versions_used[f"{scheme_code}:v{version_number}"] += 1

    # -------------------------------------------------------------
    # SUMMARY & DIAGNOSTICS EXPORT
    # -------------------------------------------------------------

    def get_metrics_summary(self) -> Dict[str, Any]:
        with self._mutex:
            uptime_seconds = round(time.time() - self._start_time, 1)

            # API latency percentiles
            req_lats = sorted(self._request_latencies) if self._request_latencies else [0]
            n_req = len(req_lats)
            p50 = req_lats[int(n_req * 0.50)]
            p95 = req_lats[int(n_req * 0.95)] if n_req > 20 else req_lats[-1]
            p99 = req_lats[int(n_req * 0.99)] if n_req > 100 else req_lats[-1]
            avg_req = sum(req_lats) / n_req if n_req else 0

            # LLM latency
            llm_lats = list(self._llm_latencies)
            avg_llm = sum(llm_lats) / len(llm_lats) if llm_lats else 0

            # Retrieval latency
            ret_lats = list(self._retrieval_latencies)
            avg_ret = sum(ret_lats) / len(ret_lats) if ret_lats else 0

            # Rule latency
            r_lats = list(self._rule_latencies)
            avg_rule = sum(r_lats) / len(r_lats) if r_lats else 0

            return {
                "system": {
                    "status": "OPERATIONAL",
                    "uptime_seconds": uptime_seconds,
                    "uptime_formatted": f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m {int(uptime_seconds % 60)}s",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
                "api_traffic": {
                    "total_requests": self._total_requests,
                    "status_distribution": dict(self._status_code_counts),
                    "latency_ms": {
                        "p50": round(p50, 2),
                        "p95": round(p95, 2),
                        "p99": round(p99, 2),
                        "avg": round(avg_req, 2),
                        "max": round(req_lats[-1], 2)
                    }
                },
                "llm_observability": {
                    "total_calls": self._total_llm_calls,
                    "error_count": self._llm_errors,
                    "avg_latency_ms": round(avg_llm, 2),
                    "prompt_tokens_estimated": self._total_prompt_tokens,
                    "completion_tokens_estimated": self._total_completion_tokens,
                    "total_tokens": self._total_prompt_tokens + self._total_completion_tokens,
                    "models_distribution": dict(self._llm_models_used)
                },
                "retrieval_observability": {
                    "total_queries": self._total_retrieval_queries,
                    "avg_latency_ms": round(avg_ret, 2),
                    "most_cited_evidence_chunk_ids": dict(self._retrieved_evidence_ids.most_common(10))
                },
                "rule_engine_observability": {
                    "total_evaluations": self._total_rule_evaluations,
                    "status_distribution": dict(self._rule_status_distribution),
                    "avg_latency_ms": round(avg_rule, 2),
                    "unknown_frequency_by_rule": dict(self._unknown_rule_reasons.most_common(10))
                },
                "fallbacks_and_anomalies": {
                    "total_fallbacks_triggered": self._total_fallbacks,
                    "reasons": dict(self._fallback_reasons)
                },
                "background_jobs": {
                    "total_jobs": self._total_background_jobs,
                    "status_distribution": dict(self._job_status_counts),
                    "avg_duration_sec": round(sum(self._job_durations) / len(self._job_durations), 2) if self._job_durations else 0.0
                },
                "policy_versions_active": dict(self._policy_versions_used)
            }

    def get_recent_traces(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._mutex:
            return list(self._recent_traces)[:limit]

    def reset_for_tests(self):
        """Allows test isolation."""
        with self._mutex:
            self._init_metrics()
