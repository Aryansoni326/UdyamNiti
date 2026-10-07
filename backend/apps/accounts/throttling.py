"""
API Rate Limiting & Throttling Policies.
Protects compute-intensive AI endpoints, authentication endpoints, and file upload endpoints
against brute-force attacks and denial-of-service attempts.
"""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """
    Limits authentication attempts (login, password reset) to prevent brute-force credential stuffing.
    Default: 5 requests per minute.
    """
    scope = 'auth'
    rate = '5/min'


class AIOrchestrationRateThrottle(UserRateThrottle):
    """
    Protects compute-heavy AI orchestrator, policy synthesis, and RAG pipelines.
    Default: 10 requests per minute per authenticated user.
    """
    scope = 'ai_orchestration'
    rate = '10/min'


class UploadRateThrottle(UserRateThrottle):
    """
    Limits document and certificate uploads.
    Default: 15 uploads per minute.
    """
    scope = 'uploads'
    rate = '15/min'


class PublicCatalogRateThrottle(AnonRateThrottle):
    """
    Limits unauthenticated public scheme browsing.
    Default: 60 requests per minute.
    """
    scope = 'public_catalog'
    rate = '60/min'
