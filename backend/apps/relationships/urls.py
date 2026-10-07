from django.urls import path
from .views import (
    relationships_list,
    can_combine_schemes,
    relationships_graph,
    seed_demo_relationships
)

urlpatterns = [
    path('relationships/', relationships_list, name='relationships-list'),
    path('relationships/can-combine/', can_combine_schemes, name='relationships-can-combine'),
    path('relationships/graph/', relationships_graph, name='relationships-graph'),
    path('relationships/seed-demo/', seed_demo_relationships, name='relationships-seed-demo'),
]
