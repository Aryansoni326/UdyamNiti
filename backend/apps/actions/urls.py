from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActionTaskViewSet, ApplicationPreparationWorkspaceViewSet

router = DefaultRouter()
router.register('actions', ActionTaskViewSet, basename='action')
router.register('workspaces', ApplicationPreparationWorkspaceViewSet, basename='workspace')
router.register('workspace', ApplicationPreparationWorkspaceViewSet, basename='workspace_singular')

urlpatterns = [
    path('', include(router.urls)),
]

