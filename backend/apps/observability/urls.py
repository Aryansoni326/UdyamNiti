"""
URL Routing for Observability, Health Probes, and Diagnostics.
"""
from django.urls import path
from .views import (
    health_liveness_view,
    health_readiness_view,
    diagnostics_api_view,
    diagnostics_dashboard_view,
    prototype_metrics_api_view,
    prototype_metrics_dashboard_view
)

urlpatterns = [
    # Health Probes
    path('health/', health_liveness_view, name='health_liveness'),
    path('health/ready/', health_readiness_view, name='health_readiness'),
    path('api/v1/health/', health_liveness_view, name='api_health_liveness'),
    path('api/v1/health/ready/', health_readiness_view, name='api_health_readiness'),
    # Diagnostics API
    path('api/v1/diagnostics/', diagnostics_api_view, name='diagnostics_api'),
    path('diagnostics/', diagnostics_dashboard_view, name='diagnostics_dashboard'),
    # Empirical Prototype Test Results
    path('api/v1/prototype-metrics/', prototype_metrics_api_view, name='prototype_metrics_api'),
    path('prototype-metrics/', prototype_metrics_dashboard_view, name='prototype_metrics_dashboard'),
]


