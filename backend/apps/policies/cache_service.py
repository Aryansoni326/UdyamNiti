"""
High-Performance Scheme Metadata & Rules Cache Service.
Eliminates repeated DB queries for static/semi-static government policy definitions.
Caches active schemes, pre-sorted rules, and cross-scheme relationship topologies.
Provides automated cache invalidation via post_save/post_delete signals.
"""
import logging
from typing import List, Dict, Optional, Any
from functools import lru_cache
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)

CACHE_TTL_SCHEMES = 3600  # 1 hour
CACHE_KEY_ACTIVE_SCHEMES = "udyamniti_cache_active_schemes_v1"
CACHE_KEY_RULES_MAP = "udyamniti_cache_rules_map_v1"
CACHE_KEY_RELATIONSHIPS_GRAPH = "udyamniti_cache_relationships_graph_v1"


class SchemeCacheService:
    """Service providing fast cached access to schemes and their deterministic rules."""

    @classmethod
    def get_active_schemes(cls) -> List[Any]:
        """
        Retrieves all active schemes with prefetched rules from cache.
        If cache miss, queries DB with prefetch_related, caches, and returns.
        """
        from apps.policies.models import Scheme

        cached_schemes = cache.get(CACHE_KEY_ACTIVE_SCHEMES)
        if cached_schemes is not None:
            return cached_schemes

        # Cache miss: Batch load with prefetch
        schemes = list(
            Scheme.objects.filter(status='active')
            .prefetch_related('rules', 'benefits')
            .order_by('name')
        )
        cache.set(CACHE_KEY_ACTIVE_SCHEMES, schemes, timeout=CACHE_TTL_SCHEMES)
        logger.debug(f"[CacheService] Loaded and cached {len(schemes)} active schemes.")
        return schemes

    @classmethod
    def get_schemes_by_codes(cls, scheme_codes: List[str]) -> List[Any]:
        """
        Returns active schemes matching a list of scheme codes from cache.
        """
        active_schemes = cls.get_active_schemes()
        code_set = set(scheme_codes)
        return [s for s in active_schemes if s.scheme_code in code_set]

    @classmethod
    def get_rules_for_scheme(cls, scheme_id: str) -> List[Any]:
        """
        Returns active rules for a scheme, ordered by order and importance.
        Served directly from memory or prefetched cache.
        """
        rules_map = cache.get(CACHE_KEY_RULES_MAP)
        if rules_map is not None and str(scheme_id) in rules_map:
            return rules_map[str(scheme_id)]

        from apps.policies.models import SchemeRule
        rules = list(
            SchemeRule.objects.filter(scheme_id=scheme_id, is_active=True)
            .order_by('order', 'importance')
        )
        return rules

    @classmethod
    def get_relationships_topology(cls) -> List[Dict[str, Any]]:
        """
        Returns all verified cross-scheme stacking and prerequisite relationships from cache.
        """
        cached_rels = cache.get(CACHE_KEY_RELATIONSHIPS_GRAPH)
        if cached_rels is not None:
            return cached_rels

        from apps.relationships.models import SchemeRelationship
        relationships = list(
            SchemeRelationship.objects.select_related('scheme_a', 'scheme_b').all()
        )
        data = [
            {
                "id": str(r.id),
                "type": r.relationship_type,
                "scheme_a_id": str(r.scheme_a_id),
                "scheme_a_code": r.scheme_a.scheme_code,
                "scheme_a_name": r.scheme_a.name,
                "scheme_b_id": str(r.scheme_b_id),
                "scheme_b_code": r.scheme_b.scheme_code,
                "scheme_b_name": r.scheme_b.name,
                "description": r.description,
            }
            for r in relationships
        ]
        cache.set(CACHE_KEY_RELATIONSHIPS_GRAPH, data, timeout=CACHE_TTL_SCHEMES)
        return data

    @classmethod
    def invalidate_all(cls):
        """Invalidates all scheme metadata caches."""
        cache.delete(CACHE_KEY_ACTIVE_SCHEMES)
        cache.delete(CACHE_KEY_RULES_MAP)
        cache.delete(CACHE_KEY_RELATIONSHIPS_GRAPH)
        logger.info("[CacheService] Invalidated active scheme, rules, and relationships caches.")


# ─── Automatic Invalidation Signals ──────────────────────────────────────────

def _handle_scheme_mutation(sender, **kwargs):
    SchemeCacheService.invalidate_all()

try:
    from apps.policies.models import Scheme, SchemeRule
    from apps.relationships.models import SchemeRelationship

    post_save.connect(_handle_scheme_mutation, sender=Scheme, weak=False)
    post_delete.connect(_handle_scheme_mutation, sender=Scheme, weak=False)
    post_save.connect(_handle_scheme_mutation, sender=SchemeRule, weak=False)
    post_delete.connect(_handle_scheme_mutation, sender=SchemeRule, weak=False)
    post_save.connect(_handle_scheme_mutation, sender=SchemeRelationship, weak=False)
    post_delete.connect(_handle_scheme_mutation, sender=SchemeRelationship, weak=False)
except Exception:
    pass
