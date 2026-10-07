from django.urls import path
from .views import (
    execute_policy_diff,
    policy_changes_list,
    approve_policy_change,
    reject_policy_change,
    evaluate_change_impact,
    profile_impact_list,
    simulate_demo_impact
)

urlpatterns = [
    path('policy-monitoring/diff/', execute_policy_diff, name='policy-diff-execute'),
    path('policy-monitoring/changes/', policy_changes_list, name='policy-changes-list'),
    path('policy-changes/', policy_changes_list, name='policy-changes-alias'),
    path('policy-monitoring/changes/<uuid:pk>/approve/', approve_policy_change, name='policy-change-approve'),
    path('policy-monitoring/changes/<uuid:pk>/reject/', reject_policy_change, name='policy-change-reject'),
    path('policy-monitoring/impact/evaluate/', evaluate_change_impact, name='policy-impact-evaluate'),
    path('policy-monitoring/impact/profile/<uuid:profile_id>/', profile_impact_list, name='policy-impact-profile-list'),
    path('policy-monitoring/impact/demo-simulate/', simulate_demo_impact, name='policy-impact-demo-simulate'),
]
