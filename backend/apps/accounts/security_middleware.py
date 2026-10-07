"""
Custom Security Middleware for UdyamNiti.
Injects production-grade HTTP security headers:
- HSTS (HTTP Strict Transport Security)
- Content Security Policy (CSP)
- X-Content-Type-Options (nosniff)
- X-Frame-Options (DENY)
- Referrer-Policy
- Permissions-Policy
Also manages request IP extraction and security audit logging.
"""
from django.utils.deprecation import MiddlewareMixin
from .models import SecurityAuditLog, AuditAction


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Ensures every response emitted by the Django backend contains hardened security headers.
    """
    def process_response(self, request, response):
        # 1. HSTS (Strict-Transport-Security) - Enforce HTTPS for 1 year
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

        # 2. Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'

        # 3. Clickjacking Defense - Disallow framing anywhere
        response['X-Frame-Options'] = 'DENY'

        # 4. Strict Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # 5. Content Security Policy (CSP)
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'",  # Allow inline scripts for Vite/React dev hydration
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com data:",
            "img-src 'self' data: https: blob:",
            "connect-src 'self' https: ws: wss:",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response['Content-Security-Policy'] = "; ".join(csp_directives)

        # 6. Hardware & Feature Permissions Policy
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=(), usb=()'

        # 7. Cross-Origin Protection
        response['Cross-Origin-Opener-Policy'] = 'same-origin'

        return response


class AuditLogMiddleware(MiddlewareMixin):
    """
    Logs sensitive state-changing operations and authentication events.
    """
    SENSITIVE_PATHS = [
        '/api/v1/auth/login/',
        '/api/v1/auth/demo/',
        '/api/v1/business-profiles/',
        '/api/v1/documents/',
        '/api/v1/strategy/',
        '/api/v1/workspace/',
    ]

    def process_response(self, request, response):
        path = request.path
        if any(path.startswith(p) for p in self.SENSITIVE_PATHS) and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            user = request.user if request.user.is_authenticated else None
            status_desc = 'SUCCESS' if response.status_code < 400 else 'FAILURE'
            if response.status_code in [401, 403]:
                status_desc = 'DENIED'

            action_type = AuditAction.PROFILE_UPDATED
            if 'login' in path:
                action_type = AuditAction.LOGIN_SUCCESS if response.status_code < 400 else AuditAction.LOGIN_FAILED
            elif 'document' in path:
                action_type = AuditAction.DOCUMENT_UPLOADED if request.method == 'POST' else AuditAction.DOCUMENT_DELETED
            elif 'strategy' in path:
                action_type = AuditAction.STRATEGY_GENERATED

            # Get client IP safely
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')

            try:
                SecurityAuditLog.objects.create(
                    user=user,
                    actor_username=user.username if user else 'Anonymous',
                    action=action_type,
                    ip_address=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                    status=status_desc,
                    details={
                        'method': request.method,
                        'path': path,
                        'status_code': response.status_code
                    }
                )
            except Exception:
                # Do not block the request if audit logging encounters a database issue
                pass

        return response
