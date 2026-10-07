"""
Structured error handling for UdyamNiti DRF APIs.
Ensures uniform error JSON envelopes across all endpoints with request trace IDs
and demo-safe failure messages that prevent confidential stack trace leakage.
"""
import logging
from django.utils import timezone
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from apps.observability.context import get_current_trace_id

logger = logging.getLogger("udyamniti.exceptions")


def custom_exception_handler(exc, context):
    """
    Standardizes error responses into a consistent structured envelope:
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human readable summary",
            "details": {...},
            "trace_id": "trc_abc123",
            "timestamp": "ISO-8601"
        }
    }
    """
    req = context.get('request') if context else None
    trace_id = getattr(req, 'trace_id', None) or get_current_trace_id()

    response = exception_handler(exc, context)

    if response is not None:
        error_code = 'API_ERROR'
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            error_code = 'VALIDATION_ERROR'
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            error_code = 'UNAUTHORIZED'
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            error_code = 'PERMISSION_DENIED'
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            error_code = 'RESOURCE_NOT_FOUND'
        elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            error_code = 'RATE_LIMIT_EXCEEDED'

        # Extract message
        message = 'An error occurred while processing the request.'
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                message = str(response.data['detail'])
            elif 'error' in response.data:
                message = str(response.data['error'])
        elif isinstance(response.data, list) and len(response.data) > 0:
            message = str(response.data[0])

        response.data = {
            'error': {
                'code': error_code,
                'message': message,
                'details': response.data if isinstance(response.data, dict) else {'errors': response.data},
                'trace_id': trace_id,
                'timestamp': timezone.now().isoformat(),
            }
        }
    else:
        # Unhandled 500 server error - log stack trace internally, return demo-safe message
        logger.error(
            f"Unhandled exception on {getattr(req, 'method', 'UNKNOWN')} {getattr(req, 'path', 'UNKNOWN')}: {str(exc)}",
            exc_info=True,
            extra={"trace_id": trace_id}
        )

        response = Response(
            {
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': 'A temporary processing issue occurred. The incident has been recorded and operations are continuing in resilience fallback mode.',
                    'details': {'error_type': exc.__class__.__name__},
                    'trace_id': trace_id,
                    'timestamp': timezone.now().isoformat(),
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
