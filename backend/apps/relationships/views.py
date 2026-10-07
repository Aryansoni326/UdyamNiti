"""
Views for Cross-Scheme Relationship Intelligence.
Exposes list, graph visualization, can-combine evaluation, and demo data seeding.
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q

from apps.policies.models import Scheme
from .models import SchemeRelationship, RelationshipType
from .services import RelationshipEngine
from .demo_data import SYNTHETIC_DEMO_RELATIONSHIPS


@api_view(['GET'])
def relationships_list(request):
    """
    List verified statutory scheme relationships.
    Optional query parameters:
      - scheme_code: Filter relationships involving this scheme
      - relationship_type: Filter by COMPATIBLE, INCOMPATIBLE, PREREQUISITE, etc.
      - include_demo: 'true' (default: true) or 'false'
    """
    qs = SchemeRelationship.objects.select_related('scheme_a', 'scheme_b').all()

    scheme_code = request.query_params.get('scheme_code')
    if scheme_code:
        qs = qs.filter(
            Q(scheme_a__scheme_code=scheme_code) | Q(scheme_b__scheme_code=scheme_code)
        )

    rel_type = request.query_params.get('relationship_type')
    if rel_type:
        qs = qs.filter(relationship_type=rel_type.upper())

    include_demo = request.query_params.get('include_demo', 'true').lower() == 'true'
    if not include_demo:
        qs = qs.filter(is_demo_data=False)

    data = [
        {
            'id': str(r.id),
            'relationship_type': r.relationship_type,
            'direction': r.direction,
            'scheme_a': {
                'code': r.scheme_a.scheme_code,
                'name': r.scheme_a.name,
                'support_type': r.scheme_a.support_type
            },
            'scheme_b': {
                'code': r.scheme_b.scheme_code,
                'name': r.scheme_b.name,
                'support_type': r.scheme_b.support_type
            },
            'affected_cost_categories': r.affected_cost_categories,
            'conditions': r.conditions,
            'description': r.description,
            'source_evidence': r.source_evidence,
            'evidence_ids': r.evidence_ids,
            'policy_versions': r.policy_versions,
            'last_verified': r.last_verified.isoformat() if r.last_verified else None,
            'confidence': r.confidence,
            'is_demo_data': r.is_demo_data
        }
        for r in qs
    ]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def can_combine_schemes(request):
    """
    Evaluate multi-scheme combination query ("Can I combine these?").
    Request Body:
    {
      "scheme_codes": ["GJ-CAPITAL-2025", "GJ-INTEREST-2025"],
      "context": {"has_term_loan": true}
    }
    """
    scheme_codes = request.data.get('scheme_codes', [])
    context = request.data.get('context', {})

    if not isinstance(scheme_codes, list) or len(scheme_codes) == 0:
        return Response(
            {'error': 'scheme_codes must be a non-empty list of scheme codes.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    engine = RelationshipEngine()
    result = engine.can_combine(scheme_codes=scheme_codes, context=context)
    return Response(result.to_dict(), status=status.HTTP_200_OK)


@api_view(['GET'])
def relationships_graph(request):
    """
    Returns knowledge graph format (nodes + edges) for frontend relationship graph visualizer.
    """
    qs = SchemeRelationship.objects.select_related('scheme_a', 'scheme_b').all()
    
    nodes_map = {}
    edges = []

    for r in qs:
        # Add node A
        if r.scheme_a.scheme_code not in nodes_map:
            nodes_map[r.scheme_a.scheme_code] = {
                "id": r.scheme_a.scheme_code,
                "name": r.scheme_a.name,
                "support_type": r.scheme_a.support_type,
                "level": r.scheme_a.level
            }
        # Add node B
        if r.scheme_b.scheme_code not in nodes_map:
            nodes_map[r.scheme_b.scheme_code] = {
                "id": r.scheme_b.scheme_code,
                "name": r.scheme_b.name,
                "support_type": r.scheme_b.support_type,
                "level": r.scheme_b.level
            }

        edges.append({
            "id": str(r.id),
            "source": r.scheme_a.scheme_code,
            "target": r.scheme_b.scheme_code,
            "type": r.relationship_type,
            "direction": r.direction,
            "description": r.description,
            "is_demo_data": r.is_demo_data
        })

    return Response({
        "nodes": list(nodes_map.values()),
        "edges": edges
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def seed_demo_relationships(request):
    """
    Seeds the synthetic demonstration relationship dataset into the database.
    """
    created_count = 0
    updated_count = 0

    for item in SYNTHETIC_DEMO_RELATIONSHIPS:
        # Ensure schemes exist (or create mock scheme representation if not present)
        s_a, _ = Scheme.objects.get_or_create(
            scheme_code=item["scheme_a_code"],
            defaults={
                "name": item["scheme_a_code"].replace("-", " "),
                "ministry_department": "Official Department",
                "level": "state_gujarat" if "GJ" in item["scheme_a_code"] else "central",
                "support_type": "capital_subsidy" if "CAPITAL" in item["scheme_a_code"] else "interest_subvention",
                "status": "active"
            }
        )
        s_b, _ = Scheme.objects.get_or_create(
            scheme_code=item["scheme_b_code"],
            defaults={
                "name": item["scheme_b_code"].replace("-", " "),
                "ministry_department": "Official Department",
                "level": "state_gujarat" if "GJ" in item["scheme_b_code"] else "central",
                "support_type": "interest_subvention" if "INTEREST" in item["scheme_b_code"] else "capital_subsidy",
                "status": "active"
            }
        )

        rel, created = SchemeRelationship.objects.update_or_create(
            scheme_a=s_a,
            scheme_b=s_b,
            defaults={
                "relationship_type": item["relationship_type"],
                "direction": item["direction"],
                "affected_cost_categories": item["affected_cost_categories"],
                "conditions": item["conditions"],
                "evidence_ids": item["evidence_ids"],
                "policy_versions": item["policy_versions"],
                "description": item["description"],
                "source_evidence": item["source_evidence"],
                "confidence": item["confidence"],
                "is_demo_data": True
            }
        )
        if created:
            created_count += 1
        else:
            updated_count += 1

    return Response({
        "message": "Synthetic demo relationships seeded successfully.",
        "created_count": created_count,
        "updated_count": updated_count,
        "total_records": len(SYNTHETIC_DEMO_RELATIONSHIPS)
    }, status=status.HTTP_200_OK)
