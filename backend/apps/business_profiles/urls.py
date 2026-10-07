from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessProfileViewSet, BusinessGoalViewSet

router = DefaultRouter()
router.register('profiles', BusinessProfileViewSet, basename='profile')
router.register('goals', BusinessGoalViewSet, basename='goal')

urlpatterns = [
    path('', include(router.urls)),
]
