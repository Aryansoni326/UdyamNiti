"""
Custom Authentication Classes for UdyamNiti.
"""
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication that skips CSRF checks for REST API requests.
    CORS origin enforcement protects browser clients while preventing
    spurious CSRF 403 failures on API endpoints.
    """
    def enforce_csrf(self, request):
        return  # Skip CSRF verification for REST requests
