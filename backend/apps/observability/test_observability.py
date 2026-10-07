"""
Comprehensive Observability, Telemetry & Health Test Suite.
Tests:
1. Request Trace ID generation and header reflection (X-Trace-ID).
2. API latency measurement and X-Response-Time-MS header.
3. Structured JSON log formatting and secret/password redaction.
4. ObservabilityRegistry telemetry tracking (LLM tokens, latency, rule evaluations, fallbacks).
5. Liveness and Readiness health probes (/health/, /health/ready/).
6. Diagnostics JSON endpoint and visual HTML dashboard (/api/v1/diagnostics/, /diagnostics/).
7. Demo-safe failure handling without leaking stack traces.
"""
import json
import logging
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.observability.context import get_current_trace_id, set_current_trace_id, clear_current_trace_id
from apps.observability.logging_formatter import StructuredJSONFormatter
from apps.observability.metrics import ObservabilityRegistry
from apps.observability.health import HealthCheckService
from config.exceptions import custom_exception_handler


class TraceIdAndMiddlewareTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        clear_current_trace_id()
        ObservabilityRegistry().reset_for_tests()

    def test_trace_id_generated_and_returned_in_headers(self):
        """Requests without trace header receive an auto-generated X-Trace-ID header."""
        res = self.client.get('/health/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('X-Trace-ID', res.headers)
        self.assertTrue(res.headers['X-Trace-ID'].startswith('trc_'))
        self.assertIn('X-Response-Time-MS', res.headers)

    def test_client_supplied_trace_id_preserved(self):
        """If client provides X-Trace-ID header, it is preserved throughout the pipeline."""
        custom_trace = "client-trace-uuid-9999"
        res = self.client.get('/health/', HTTP_X_TRACE_ID=custom_trace)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.headers.get('X-Trace-ID'), custom_trace)

    def test_metrics_middleware_records_traffic(self):
        """Requests are recorded in ObservabilityRegistry."""
        self.client.get('/health/')
        self.client.get('/health/')
        summary = ObservabilityRegistry().get_metrics_summary()
        self.assertGreaterEqual(summary['api_traffic']['total_requests'], 2)
        self.assertIn('200', summary['api_traffic']['status_distribution'])


class StructuredJSONFormatterTestCase(TestCase):
    def setUp(self):
        self.formatter = StructuredJSONFormatter()
        set_current_trace_id("test_trace_12345")

    def tearDown(self):
        clear_current_trace_id()

    def test_formats_valid_json_with_standard_fields(self):
        """Log record outputs valid JSON containing timestamp, level, trace_id, and message."""
        record = logging.LogRecord(
            name="udyamniti.test",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Evaluating policy rules for enterprise",
            args=(),
            exc_info=None
        )
        formatted = self.formatter.format(record)
        data = json.loads(formatted)

        self.assertEqual(data["level"], "INFO")
        self.assertEqual(data["logger"], "udyamniti.test")
        self.assertEqual(data["trace_id"], "test_trace_12345")
        self.assertIn("Evaluating policy rules", data["message"])
        self.assertIn("timestamp", data)

    def test_redacts_sensitive_passwords_and_tokens(self):
        """Passwords, bearer tokens, and sensitive keys are masked."""
        record = logging.LogRecord(
            name="udyamniti.security",
            level=logging.WARNING,
            pathname="test_file.py",
            lineno=50,
            msg="Failed attempt with password 'SuperSecret123!' and Bearer eyJhbGciOiJIUzI1NiJ9",
            args=(),
            exc_info=None
        )
        record.password = "SuperSecret123!"
        record.auth_token = "secret_token_val"

        formatted = self.formatter.format(record)
        data = json.loads(formatted)

        # Message sanitized
        self.assertNotIn("SuperSecret123!", data["message"])
        self.assertNotIn("eyJhbGciOiJIUzI1NiJ9", data["message"])

        # Dict attributes sanitized
        self.assertEqual(data.get("password"), "[REDACTED]")
        self.assertEqual(data.get("auth_token"), "[REDACTED]")


class MetricsRegistryTestCase(TestCase):
    def setUp(self):
        self.registry = ObservabilityRegistry()
        self.registry.reset_for_tests()

    def test_llm_metrics_recording(self):
        """Recording LLM calls computes latencies and token usage."""
        self.registry.record_llm_call(
            model_name="gemini-1.5-flash",
            duration_ms=450.0,
            prompt_tokens=300,
            completion_tokens=150,
            success=True
        )
        self.registry.record_llm_call(
            model_name="gemini-1.5-flash",
            duration_ms=550.0,
            prompt_tokens=250,
            completion_tokens=100,
            success=True
        )

        summary = self.registry.get_metrics_summary()
        llm = summary["llm_observability"]
        self.assertEqual(llm["total_calls"], 2)
        self.assertEqual(llm["avg_latency_ms"], 500.0)
        self.assertEqual(llm["prompt_tokens_estimated"], 550)
        self.assertEqual(llm["completion_tokens_estimated"], 250)
        self.assertEqual(llm["total_tokens"], 800)

    def test_retrieval_and_evidence_ids_tracking(self):
        """Evidence chunk IDs and retrieval latencies are tracked."""
        self.registry.record_retrieval(
            duration_ms=25.0,
            candidate_count=3,
            evidence_chunk_ids=["chk-pmegp-01", "chk-pmegp-02"]
        )
        self.registry.record_retrieval(
            duration_ms=35.0,
            candidate_count=2,
            evidence_chunk_ids=["chk-pmegp-01", "chk-gujarat-01"]
        )

        summary = self.registry.get_metrics_summary()
        ret = summary["retrieval_observability"]
        self.assertEqual(ret["total_queries"], 2)
        self.assertEqual(ret["avg_latency_ms"], 30.0)
        self.assertEqual(ret["most_cited_evidence_chunk_ids"]["chk-pmegp-01"], 2)
        self.assertEqual(ret["most_cited_evidence_chunk_ids"]["chk-gujarat-01"], 1)

    def test_rule_evaluations_and_fallback_tracking(self):
        """Rule engine status breakdown and fallback reasons are recorded."""
        self.registry.record_rule_evaluation("Turnover Check", "PMEGP", "MATCH", 2.0)
        self.registry.record_rule_evaluation("Location Check", "PMEGP", "MATCH", 1.5)
        self.registry.record_rule_evaluation("Investment Check", "PMEGP", "UNKNOWN", 1.0, reason="Plant cost unverified")
        self.registry.record_fallback("GroundedEvidenceComposer", "LLM offline, using deterministic synthesizer")

        summary = self.registry.get_metrics_summary()
        rule = summary["rule_engine_observability"]
        self.assertEqual(rule["total_evaluations"], 3)
        self.assertEqual(rule["status_distribution"]["MATCH"], 2)
        self.assertEqual(rule["status_distribution"]["UNKNOWN"], 1)

        fallbacks = summary["fallbacks_and_anomalies"]
        self.assertEqual(fallbacks["total_fallbacks_triggered"], 1)


class HealthAndDiagnosticsEndpointsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_liveness_endpoint(self):
        """GET /health/ returns 200 OK with status healthy."""
        res = self.client.get('/health/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('status'), 'healthy')

    def test_health_readiness_endpoint(self):
        """GET /health/ready/ checks database and components."""
        res = self.client.get('/health/ready/')
        self.assertIn(res.status_code, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])
        self.assertIn('components', res.data)
        self.assertIn('database', res.data['components'])
        self.assertIn('vector_embeddings', res.data['components'])

    def test_diagnostics_api_endpoint(self):
        """GET /api/v1/diagnostics/ returns structured metrics summary and trace list."""
        res = self.client.get('/api/v1/diagnostics/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('system', res.data)
        self.assertIn('api_traffic', res.data)
        self.assertIn('llm_observability', res.data)
        self.assertIn('recent_traces', res.data)

    def test_diagnostics_dashboard_html_view(self):
        """GET /diagnostics/ returns 200 HTML with telemetry elements."""
        res = self.client.get('/diagnostics/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('text/html', res['Content-Type'])
        content = res.content.decode('utf-8')
        self.assertIn('UdyamNiti System Telemetry & Diagnostics', content)
        self.assertIn('Component Readiness', content)
        self.assertIn('Recent Request Traces', content)


class DemoSafeFailureHandlingTestCase(TestCase):
    def test_unhandled_exception_returns_demo_safe_envelope(self):
        """Unhandled exceptions return a structured 500 error envelope with trace ID without stack traces."""
        class MockRequest:
            method = "POST"
            path = "/api/v1/strategy/generate/"
            trace_id = "trc_err_test_456"

        context = {"request": MockRequest()}
        exc = RuntimeError("Simulated internal AI crash or timeout")

        response = custom_exception_handler(exc, context)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        error_payload = response.data.get('error', {})
        self.assertEqual(error_payload.get('code'), 'INTERNAL_SERVER_ERROR')
        self.assertEqual(error_payload.get('trace_id'), 'trc_err_test_456')
        # Ensure raw stack trace is not exposed
        self.assertNotIn('Traceback', error_payload.get('message', ''))
        self.assertIn('resilience fallback mode', error_payload.get('message', ''))
