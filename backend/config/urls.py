"""UdyamNiti URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.business_profiles.urls')),
    path('api/v1/', include('apps.policies.urls')),
    path('api/v1/', include('apps.eligibility.urls')),
    path('api/v1/', include('apps.relationships.urls')),
    path('api/v1/', include('apps.opportunities.urls')),
    path('api/v1/', include('apps.strategy.urls')),
    path('api/v1/', include('apps.actions.urls')),
    path('api/v1/', include('apps.policy_monitoring.urls')),
    path('api/v1/', include('apps.documents.urls')),
    path('api/v1/', include('apps.rag.urls')),
    path('', include('apps.observability.urls')),
]
