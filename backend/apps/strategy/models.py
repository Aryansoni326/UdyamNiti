"""Strategy domain models."""
from django.db import models
import uuid
from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.policies.models import Scheme


class Strategy(models.Model):
    """The assembled government-support strategy for a specific business goal."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goal = models.OneToOneField(BusinessGoal, on_delete=models.CASCADE, related_name='strategy')
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='strategies')
    
    narrative = models.TextField(blank=True)
    total_opportunities = models.IntegerField(default=0)
    matched_count = models.IntegerField(default=0)
    potential_count = models.IntegerField(default=0)
    
    # Full results as JSON for API efficiency
    scheme_results = models.JSONField(default=list)
    relationships = models.JSONField(default=list)
    action_plan = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'strategies'
        ordering = ['-created_at']


class StrategyItem(models.Model):
    """A single scheme within a strategy with its status and priority."""
    PRIORITY_CHOICES = [(i, str(i)) for i in range(1, 6)]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, related_name='items')
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='strategy_items')
    
    status = models.CharField(max_length=40)
    score = models.FloatField(default=0.0)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)
    is_recommended = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'strategy_items'
        ordering = ['priority', '-score']


class OpportunityEdge(models.Model):
    """
    Directed edge in an opportunity dependency graph for a strategy.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, related_name='graph_edges')
    source_scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='outgoing_edges')
    target_scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='incoming_edges')
    relationship_type = models.CharField(max_length=40)
    edge_label = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'opportunity_edges'


class ActionPlan(models.Model):
    """
    Aggregate roadmap container holding action tasks for a strategy.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    strategy = models.OneToOneField(Strategy, on_delete=models.CASCADE, related_name='plan')
    title = models.CharField(max_length=255, default='Targeted Execution Plan')
    total_steps = models.PositiveIntegerField(default=0)
    estimated_total_weeks = models.PositiveIntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'action_plans'


class GraphNodeType(models.TextChoices):
    BUSINESS = 'Business', 'Business'
    BUSINESS_FACT = 'BusinessFact', 'Business Fact'
    GOAL = 'Goal', 'Goal'
    RULE = 'Rule', 'Rule'
    SCHEME = 'Scheme', 'Scheme'
    SCHEME_VERSION = 'SchemeVersion', 'Scheme Version'
    EVIDENCE = 'Evidence', 'Evidence'
    RELATIONSHIP = 'Relationship', 'Relationship'
    PREREQUISITE = 'Prerequisite', 'Prerequisite'
    BLOCKER = 'Blocker', 'Blocker'
    UNLOCK_ACTION = 'UnlockAction', 'Unlock Action'
    ACTION = 'Action', 'Action'


class GraphEdgeType(models.TextChoices):
    HAS_FACT = 'HAS_FACT', 'HAS_FACT'
    TARGETS_GOAL = 'TARGETS_GOAL', 'TARGETS_GOAL'
    EVALUATED_BY = 'EVALUATED_BY', 'EVALUATED_BY'
    SATISFIES = 'SATISFIES', 'SATISFIES'
    FAILS = 'FAILS', 'FAILS'
    UNKNOWN_FOR = 'UNKNOWN_FOR', 'UNKNOWN_FOR'
    SUPPORTED_BY = 'SUPPORTED_BY', 'SUPPORTED_BY'
    REQUIRES = 'REQUIRES', 'REQUIRES'
    RELATES_TO = 'RELATES_TO', 'RELATES_TO'
    BLOCKS = 'BLOCKS', 'BLOCKS'
    MAY_UNLOCK = 'MAY_UNLOCK', 'MAY_UNLOCK'
    LEADS_TO = 'LEADS_TO', 'LEADS_TO'


class EvidenceGraphNode(models.Model):
    """
    Relational graph node representing an entity in the statutory decision chain.
    """
    id = models.CharField(max_length=255, primary_key=True)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, related_name='evidence_nodes', null=True, blank=True)
    node_type = models.CharField(max_length=50, choices=GraphNodeType.choices)
    label = models.CharField(max_length=500)
    properties = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'evidence_graph_nodes'
        indexes = [
            models.Index(fields=['node_type']),
            models.Index(fields=['strategy']),
        ]

    def __str__(self):
        return f"[{self.node_type}] {self.label}"


class EvidenceGraphEdge(models.Model):
    """
    Directed relational graph edge representing a statutory or causal dependency.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, related_name='evidence_edges', null=True, blank=True)
    source = models.ForeignKey(EvidenceGraphNode, on_delete=models.CASCADE, related_name='outgoing_edges')
    target = models.ForeignKey(EvidenceGraphNode, on_delete=models.CASCADE, related_name='incoming_edges')
    edge_type = models.CharField(max_length=50, choices=GraphEdgeType.choices)
    label = models.CharField(max_length=255, blank=True)
    properties = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'evidence_graph_edges'
        indexes = [
            models.Index(fields=['edge_type']),
            models.Index(fields=['source', 'target']),
            models.Index(fields=['strategy']),
        ]

    def __str__(self):
        return f"{self.source_id} -[{self.edge_type}]-> {self.target_id}"

