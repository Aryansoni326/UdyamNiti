from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OpportunityUnlockViewSet

router = DefaultRouter()
router.register('unlocks', OpportunityUnlockViewSet, basename='unlock')

urlpatterns = [
    path('', include(router.urls)),
]
