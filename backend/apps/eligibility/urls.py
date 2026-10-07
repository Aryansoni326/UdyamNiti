from django.urls import path
from apps.eligibility.views import (
    SingleSchemeEvaluateAPIView,
    BatchEvaluateAPIView,
    ReEvaluateAPIView
)

urlpatterns = [
    path('evaluate/', SingleSchemeEvaluateAPIView.as_view(), name='eligibility-evaluate'),
    path('evaluate-batch/', BatchEvaluateAPIView.as_view(), name='eligibility-evaluate-batch'),
    path('re-evaluate/', ReEvaluateAPIView.as_view(), name='eligibility-re-evaluate'),
]
