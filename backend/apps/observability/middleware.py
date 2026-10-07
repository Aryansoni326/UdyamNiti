"""
Observability Middleware for Request Tracing and Performance Telemetry.
1. TraceIdMiddleware: Injects unique request trace ID, sets thread context, and attaches X-Trace-ID header.
2. ObservabilityMetricsMiddleware: Measures API response latencies, records status codes, and registers metrics.
"""
import time
import uuid
import logging
from django.utils.deprecation import MiddlewareMixin
from .context import set_current_trace_id, clear_current_trace_id, set_current_user_id
from .metrics import ObservabilityRegistry

logger = logging.getLogger("udyamniti.telemetry")


class TraceIdMiddleware(MiddlewareMixin):
    """
    Guarantees every HTTP request has an unambiguous trace ID propagated across all services,
    log messages, and response headers.
    """
    HEADER_TRACE_ID = 'HTTP_X_TRACE_ID'
    HEADER_REQUEST_ID = 'HTTP_X_REQUEST_ID'
    HEADER_CORRELATION_ID = 'HTTP_X_CORRELATION_ID'

    def process_request(self, request):
        # Read from incoming client header (correlation ID, trace ID, or request ID) or generate new ID
        trace_id = (
            request.META.get(self.HEADER_CORRELATION_ID) or
            request.META.get(self.HEADER_TRACE_ID) or
            request.META.get(self.HEADER_REQUEST_ID) or
            f"trc_{uuid.uuid4().hex[:12]}"
        )
        request.trace_id = trace_id
        request.correlation_id = trace_id
        set_current_trace_id(trace_id)

        # Track authenticated user if present
        if hasattr(request, 'user') and request.user.is_authenticated:
            set_current_user_id(str(request.user.id))
        else:
            set_current_user_id(None)

    def process_response(self, request, response):
        trace_id = getattr(request, 'trace_id', None) or getattr(request, 'correlation_id', None)
        if trace_id:
            response['X-Trace-ID'] = trace_id
            response['X-Correlation-ID'] = trace_id
        return response


class ObservabilityMetricsMiddleware(MiddlewareMixin):
    """
    Measures endpoint latency, records telemetry into ObservabilityRegistry,
    and emits structured audit logs.
    """
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.registry = ObservabilityRegistry()

    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        start_time = getattr(request, '_start_time', None)
        duration_ms = 0.0
        if start_time:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            response['X-Response-Time-MS'] = str(duration_ms)

        trace_id = getattr(request, 'trace_id', 'unknown_trace')
        user_id = str(request.user.id) if hasattr(request, 'user') and request.user.is_authenticated else None

        error_summary = None
        if response.status_code >= 400:
            error_summary = f"HTTP {response.status_code} on {request.method} {request.path}"

        # Record metric in registry
        self.registry.record_request(
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            trace_id=trace_id,
            user_id=user_id,
            error_summary=error_summary
        )

        # Log request summary
        log_level = logging.INFO
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING

        logger.log(
            log_level,
            f"{request.method} {request.path} {response.status_code} ({duration_ms}ms)",
            extra={
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "trace_id": trace_id
            }
        )

        # Clean up thread context
        clear_current_trace_id()

        return response
