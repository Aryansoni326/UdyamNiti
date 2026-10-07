"""
Evidence Graph Service & Traceability Engine.
Constructs and queries the statutory 'Why?' causal graph:
Business Fact -> Rule -> Scheme -> Official Evidence -> Result -> Relationship/Blocker -> Action.
Implemented over PostgreSQL relational tables (EvidenceGraphNode & EvidenceGraphEdge).
"""
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from django.db import transaction

from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.policies.models import Scheme
from apps.eligibility.models import EligibilityEvaluation
from apps.relationships.models import SchemeRelationship
from apps.opportunities.models import OpportunityUnlock
from apps.actions.models import ActionTask
from apps.strategy.models import (
    Strategy,
    EvidenceGraphNode,
    EvidenceGraphEdge,
    GraphNodeType,
    GraphEdgeType
)

logger = logging.getLogger(__name__)


class EvidenceGraphService:
    """
    Manages the Knowledge Graph of policy decisions, ensuring end-to-end statutory traceability.
    """

    def build_or_update_graph(self, strategy: Strategy) -> Tuple[int, int]:
        """
        Materializes or synchronizes the Evidence Graph for a Strategy into PostgreSQL tables.
        Returns (nodes_count, edges_count).
        """
        profile = strategy.business_profile
        goal = strategy.goal

        nodes: Dict[str, EvidenceGraphNode] = {}
        edges_data: List[Dict[str, Any]] = []

        # Helper to create/register nodes in memory
        def add_node(node_id: str, node_type: str, label: str, properties: Dict[str, Any] = None) -> EvidenceGraphNode:
            if node_id not in nodes:
                nodes[node_id] = EvidenceGraphNode(
                    id=node_id,
                    strategy=strategy,
                    node_type=node_type,
                    label=label[:500],
                    properties=properties or {}
                )
            return nodes[node_id]

        def add_edge(source_id: str, target_id: str, edge_type: str, label: str = "", properties: Dict[str, Any] = None):
            edges_data.append({
                "source_id": source_id,
                "target_id": target_id,
                "edge_type": edge_type,
                "label": label,
                "properties": properties or {}
            })

        # 1. Business Node
        biz_id = f"urn:node:business:{profile.id}"
        add_node(biz_id, GraphNodeType.BUSINESS, profile.business_name, {
            "entity_type": profile.entity_type,
            "msme_category": profile.msme_category,
            "state": profile.state
        })

        # 2. Business Fact Nodes
        facts = [
            ("investment", f"Plant & Machinery Investment: ₹{profile.investment_in_plant_machinery_lakhs} Lakhs", {"amount_lakhs": float(profile.investment_in_plant_machinery_lakhs or 0)}),
            ("turnover", f"Annual Turnover: ₹{profile.annual_turnover_lakhs} Lakhs", {"amount_lakhs": float(profile.annual_turnover_lakhs or 0)}),
            ("msme_category", f"MSME Category: {profile.msme_category.upper() if profile.msme_category else 'UNKNOWN'}", {"category": profile.msme_category}),
            ("location", f"Location: {profile.district}, {profile.state}", {"state": profile.state, "district": profile.district}),
            ("udyam_status", f"Udyam Registered: {'Yes (' + profile.udyam_registration_number + ')' if profile.udyam_registration_number else 'No'}", {"has_udyam": bool(profile.udyam_registration_number)}),
            ("women_owned", f"Women Owned: {'Yes' if profile.is_women_owned else 'No'}", {"is_women_owned": profile.is_women_owned}),
            ("sc_st_owned", f"SC/ST Owned: {'Yes' if profile.is_sc_st_owned else 'No'}", {"is_sc_st_owned": profile.is_sc_st_owned}),
        ]

        fact_id_map = {}
        for f_key, f_label, f_props in facts:
            fact_id = f"urn:node:fact:{profile.id}:{f_key}"
            fact_id_map[f_key] = fact_id
            add_node(fact_id, GraphNodeType.BUSINESS_FACT, f_label, f_props)
            add_edge(biz_id, fact_id, GraphEdgeType.HAS_FACT, "Has Fact")

        # 3. Goal Node
        goal_id = f"urn:node:goal:{goal.id}"
        add_node(goal_id, GraphNodeType.GOAL, goal.parsed_objective or goal.raw_goal_text[:80], {
            "project_type": goal.parsed_project_type,
            "investment_lakhs": float(goal.parsed_investment_amount_lakhs or 0),
            "support_categories": goal.parsed_support_categories
        })
        add_edge(biz_id, goal_id, GraphEdgeType.TARGETS_GOAL, "Targets Goal")

        # 4. Evaluations & Scheme Nodes
        evaluations = EligibilityEvaluation.objects.filter(goal=goal).select_related('scheme')
        for ev in evaluations:
            scheme = ev.scheme
            scheme_id = f"urn:node:scheme:{scheme.scheme_code}"
            add_node(scheme_id, GraphNodeType.SCHEME, scheme.name, {
                "scheme_code": scheme.scheme_code,
                "support_type": scheme.support_type,
                "level": scheme.level,
                "overall_status": ev.overall_status,
                "score": ev.score,
                "max_benefit_lakhs": float(scheme.max_benefit_amount_lakhs or 0)
            })

            # SchemeVersion Node
            version_id = f"urn:node:scheme_version:{scheme.scheme_code}:current"
            add_node(version_id, GraphNodeType.SCHEME_VERSION, f"Active Gazette Policy v2025.1", {
                "effective_until": "2027-12-31"
            })
            add_edge(scheme_id, version_id, GraphEdgeType.EVALUATED_BY, "Enacted Under")

            # Connect Goal to Scheme
            add_edge(goal_id, scheme_id, GraphEdgeType.EVALUATED_BY, f"Evaluated (Status: {ev.overall_status})")

            # Conditions & Rules
            for idx, c in enumerate(ev.condition_results or []):
                rule_key = c.get('rule_id') or f"rule_{idx}"
                rule_id = f"urn:node:rule:{scheme.scheme_code}:{rule_key}"
                rule_label = c.get('display_label') or c.get('rule_name') or f"Rule {rule_key}"
                c_status = c.get('status', 'UNKNOWN').upper()

                add_node(rule_id, GraphNodeType.RULE, rule_label, {
                    "rule_id": rule_key,
                    "status": c_status,
                    "explanation": c.get('explanation', ''),
                    "importance": c.get('importance', 'mandatory'),
                    "source_clause": c.get('source_clause', '')
                })

                # Rule -> Scheme
                add_edge(rule_id, scheme_id, GraphEdgeType.EVALUATED_BY, f"Governs Condition ({c_status})")

                # Map relevant fact to rule
                mapped_fact_id = fact_id_map.get("investment")  # default fallback
                rule_name_lower = rule_label.lower()
                if "investment" in rule_name_lower:
                    mapped_fact_id = fact_id_map.get("investment")
                elif "turnover" in rule_name_lower:
                    mapped_fact_id = fact_id_map.get("turnover")
                elif "udyam" in rule_name_lower or "registration" in rule_name_lower:
                    mapped_fact_id = fact_id_map.get("udyam_status")
                elif "state" in rule_name_lower or "location" in rule_name_lower:
                    mapped_fact_id = fact_id_map.get("location")
                elif "women" in rule_name_lower:
                    mapped_fact_id = fact_id_map.get("women_owned")
                elif "category" in rule_name_lower or "msme" in rule_name_lower:
                    mapped_fact_id = fact_id_map.get("msme_category")

                if mapped_fact_id:
                    if c_status in ("PASS", "SATISFIED"):
                        add_edge(mapped_fact_id, rule_id, GraphEdgeType.SATISFIES, "Satisfies Condition")
                    elif c_status in ("FAIL", "NOT_SATISFIED"):
                        add_edge(mapped_fact_id, rule_id, GraphEdgeType.FAILS, "Fails Condition")
                    else:
                        add_edge(mapped_fact_id, rule_id, GraphEdgeType.UNKNOWN_FOR, "Verification Required")

                # Official Evidence Node for this rule/clause
                clause_ref = c.get('source_clause') or "Statutory Resolution"
                evidence_id = f"urn:node:evidence:{scheme.scheme_code}:{rule_key}"
                add_node(evidence_id, GraphNodeType.EVIDENCE, f"Statutory Clause: {clause_ref}", {
                    "clause_ref": clause_ref,
                    "official_portal_url": scheme.official_portal_url or ""
                })
                add_edge(rule_id, evidence_id, GraphEdgeType.SUPPORTED_BY, "Grounded In Evidence")
                add_edge(scheme_id, evidence_id, GraphEdgeType.SUPPORTED_BY, "Official Source")

            # Blockers if status is DOES_NOT_MATCH or has mandatory failures
            for fail_msg in (ev.mandatory_failures or []):
                blocker_id = f"urn:node:blocker:{scheme.scheme_code}:{hash(fail_msg) % 10000}"
                add_node(blocker_id, GraphNodeType.BLOCKER, f"Statutory Blocker: {fail_msg[:120]}", {
                    "reason": fail_msg
                })
                add_edge(blocker_id, scheme_id, GraphEdgeType.BLOCKS, "Blocks Eligibility")

        # 5. Cross-Scheme Relationships
        scheme_db_ids = [ev.scheme.id for ev in evaluations]
        relationships = SchemeRelationship.objects.filter(
            scheme_a__in=scheme_db_ids, scheme_b__in=scheme_db_ids
        ).select_related('scheme_a', 'scheme_b')

        for rel in relationships:
            rel_id = f"urn:node:relationship:{rel.scheme_a.scheme_code}:{rel.scheme_b.scheme_code}"
            add_node(rel_id, GraphNodeType.RELATIONSHIP, f"{rel.relationship_type}: {rel.scheme_a.scheme_code} <-> {rel.scheme_b.scheme_code}", {
                "relationship_type": rel.relationship_type,
                "direction": rel.direction,
                "tradeoff": rel.description,
                "affected_cost_categories": rel.affected_cost_categories
            })
            s_a_node = f"urn:node:scheme:{rel.scheme_a.scheme_code}"
            s_b_node = f"urn:node:scheme:{rel.scheme_b.scheme_code}"
            add_edge(s_a_node, rel_id, GraphEdgeType.RELATES_TO, rel.relationship_type)
            add_edge(rel_id, s_b_node, GraphEdgeType.RELATES_TO, rel.relationship_type)

            # If prerequisite
            if rel.relationship_type == "PREREQUISITE":
                prereq_id = f"urn:node:prerequisite:{rel.scheme_a.scheme_code}"
                add_node(prereq_id, GraphNodeType.PREREQUISITE, f"Prerequisite: {rel.scheme_a.name}", {})
                add_edge(s_b_node, prereq_id, GraphEdgeType.REQUIRES, "Requires")

        # 6. Unlock Actions
        unlocks = OpportunityUnlock.objects.filter(strategy=strategy)
        for u in unlocks:
            unlock_id = f"urn:node:unlock:{u.id}"
            add_node(unlock_id, GraphNodeType.UNLOCK_ACTION, u.title, {
                "missing_fact": u.missing_fact_key,
                "action_required": u.action_required,
                "potential_benefit_lakhs": float(u.potential_benefit_lakhs or 0)
            })
            # Connect unlock to relevant scheme or goal
            add_edge(goal_id, unlock_id, GraphEdgeType.MAY_UNLOCK, "Opportunity Unlock")

        # 7. Concrete Action Tasks
        tasks = ActionTask.objects.filter(strategy=strategy)
        for t in tasks:
            action_id = f"urn:node:action:{t.id}"
            add_node(action_id, GraphNodeType.ACTION, t.title, {
                "task_type": t.task_type,
                "priority": t.priority,
                "portal_url": t.portal_url or "",
                "estimated_days": t.estimated_days
            })
            if t.scheme:
                scheme_id = f"urn:node:scheme:{t.scheme.scheme_code}"
                add_edge(scheme_id, action_id, GraphEdgeType.LEADS_TO, "Leads To Action")
            else:
                add_edge(goal_id, action_id, GraphEdgeType.LEADS_TO, "Direct Next Step")

        # Atomic Persist to PostgreSQL tables
        with transaction.atomic():
            # Clear old records for this strategy
            EvidenceGraphEdge.objects.filter(strategy=strategy).delete()
            EvidenceGraphNode.objects.filter(strategy=strategy).delete()

            # Bulk create nodes
            EvidenceGraphNode.objects.bulk_create(list(nodes.values()), batch_size=200)

            # Build edge objects
            edge_objs = []
            for e in edges_data:
                src_node = nodes.get(e["source_id"])
                tgt_node = nodes.get(e["target_id"])
                if src_node and tgt_node:
                    edge_objs.append(EvidenceGraphEdge(
                        strategy=strategy,
                        source=src_node,
                        target=tgt_node,
                        edge_type=e["edge_type"],
                        label=e["label"],
                        properties=e["properties"]
                    ))

            EvidenceGraphEdge.objects.bulk_create(edge_objs, batch_size=200)

        logger.info(f"Built Evidence Graph for strategy {strategy.id}: {len(nodes)} nodes, {len(edge_objs)} edges.")
        return len(nodes), len(edge_objs)

    def get_why_path(self, strategy_id: str, scheme_code: str) -> Dict[str, Any]:
        """
        Reconstructs the statutory 'Why?' causal chain for a specific scheme:
        Business Fact -> Rule -> Scheme -> Official Evidence -> Result -> Relationship/Blocker -> Action.
        """
        try:
            strategy = Strategy.objects.get(id=strategy_id)
        except (Strategy.DoesNotExist, ValueError):
            return {"error": f"Strategy {strategy_id} not found."}

        # Check if nodes exist, if not, generate graph
        node_count = EvidenceGraphNode.objects.filter(strategy=strategy).count()
        if node_count == 0:
            self.build_or_update_graph(strategy)

        scheme_node_id = f"urn:node:scheme:{scheme_code}"
        scheme_node = EvidenceGraphNode.objects.filter(strategy=strategy, id=scheme_node_id).first()

        if not scheme_node:
            # Fallback: try finding by label or property
            scheme_node = EvidenceGraphNode.objects.filter(
                strategy=strategy,
                node_type=GraphNodeType.SCHEME,
                properties__scheme_code=scheme_code
            ).first()

        if not scheme_node:
            return {
                "error": f"Scheme '{scheme_code}' was not found in the Evidence Graph for this strategy.",
                "nodes": [],
                "edges": [],
                "why_path_sequence": [],
                "path_narrative": "No statutory evaluation path found."
            }

        # Step 1: Trace Rules governing this Scheme (incoming EVALUATED_BY edges)
        rule_edges = EvidenceGraphEdge.objects.filter(
            strategy=strategy,
            target=scheme_node,
            edge_type=GraphEdgeType.EVALUATED_BY,
            source__node_type=GraphNodeType.RULE
        ).select_related('source')

        rule_nodes = [e.source for e in rule_edges]

        # Step 2: Trace Business Facts satisfying/failing these Rules
        fact_edges = EvidenceGraphEdge.objects.filter(
            strategy=strategy,
            target__in=rule_nodes,
            edge_type__in=[GraphEdgeType.SATISFIES, GraphEdgeType.FAILS, GraphEdgeType.UNKNOWN_FOR]
        ).select_related('source', 'target')

        fact_nodes = list({e.source for e in fact_edges})

        # Step 3: Trace Official Evidence for Scheme & Rules
        evidence_edges = EvidenceGraphEdge.objects.filter(
            strategy=strategy,
            edge_type=GraphEdgeType.SUPPORTED_BY
        ).filter(
            source__in=[scheme_node] + rule_nodes
        ).select_related('target')

        evidence_nodes = list({e.target for e in evidence_edges})

        # Step 4: Trace Relationships & Blockers
        rel_edges = EvidenceGraphEdge.objects.filter(
            strategy=strategy,
            edge_type=GraphEdgeType.RELATES_TO,
            source=scheme_node
        ).select_related('target')

        rel_nodes = [e.target for e in rel_edges]

        blocker_edges = EvidenceGraphEdge.objects.filter(
            strategy=strategy,
            target=scheme_node,
            edge_type=GraphEdgeType.BLOCKS
        ).select_related('source')

        blocker_nodes = [e.source for e in blocker_edges]

        # Step 5: Trace Actions leading from Scheme or Unlocks
        action_edges = EvidenceGraphEdge.objects.filter(
            strategy=strategy,
            source=scheme_node,
            edge_type=GraphEdgeType.LEADS_TO
        ).select_related('target')

        action_nodes = [e.target for e in action_edges]

        # Consolidate Path Nodes
        all_path_nodes = list({
            scheme_node,
            *fact_nodes,
            *rule_nodes,
            *evidence_nodes,
            *rel_nodes,
            *blocker_nodes,
            *action_nodes
        })

        # Consolidate Path Edges
        all_node_ids = {n.id for n in all_path_nodes}
        relevant_edges = EvidenceGraphEdge.objects.filter(
            strategy=strategy,
            source_id__in=all_node_ids,
            target_id__in=all_node_ids
        )

        # Formulate Ordered Path Sequence
        # Business Fact -> Rule -> Scheme -> Official Evidence -> Result -> Relationship/Blocker -> Action
        primary_fact = fact_nodes[0].id if fact_nodes else (f"urn:node:fact:{strategy.business_profile.id}:investment")
        primary_rule = rule_nodes[0].id if rule_nodes else None
        primary_evidence = evidence_nodes[0].id if evidence_nodes else None
        primary_rel_or_blocker = (blocker_nodes[0].id if blocker_nodes else (rel_nodes[0].id if rel_nodes else None))
        primary_action = action_nodes[0].id if action_nodes else None

        path_sequence = [primary_fact]
        if primary_rule:
            path_sequence.append(primary_rule)
        path_sequence.append(scheme_node.id)
        if primary_evidence:
            path_sequence.append(primary_evidence)
        if primary_rel_or_blocker:
            path_sequence.append(primary_rel_or_blocker)
        if primary_action:
            path_sequence.append(primary_action)

        # Generate Synthesis Narrative
        overall_status = scheme_node.properties.get("overall_status", "UNKNOWN")
        path_narrative = self._generate_path_narrative(
            scheme_node=scheme_node,
            overall_status=overall_status,
            fact_nodes=fact_nodes,
            rule_nodes=rule_nodes,
            evidence_nodes=evidence_nodes,
            rel_nodes=rel_nodes,
            blocker_nodes=blocker_nodes,
            action_nodes=action_nodes
        )

        return {
            "strategy_id": str(strategy.id),
            "scheme_code": scheme_code,
            "overall_status": overall_status,
            "nodes": [
                {
                    "id": n.id,
                    "type": n.node_type,
                    "label": n.label,
                    "properties": n.properties
                }
                for n in all_path_nodes
            ],
            "edges": [
                {
                    "id": str(e.id),
                    "source": e.source_id,
                    "target": e.target_id,
                    "type": e.edge_type,
                    "label": e.label
                }
                for e in relevant_edges
            ],
            "why_path_sequence": path_sequence,
            "path_narrative": path_narrative
        }

    def get_full_graph(self, strategy_id: str) -> Dict[str, Any]:
        """
        Returns full graph JSON for frontend visualization.
        """
        try:
            strategy = Strategy.objects.get(id=strategy_id)
        except (Strategy.DoesNotExist, ValueError):
            return {"error": f"Strategy {strategy_id} not found."}

        node_count = EvidenceGraphNode.objects.filter(strategy=strategy).count()
        if node_count == 0:
            self.build_or_update_graph(strategy)

        nodes = EvidenceGraphNode.objects.filter(strategy=strategy)
        edges = EvidenceGraphEdge.objects.filter(strategy=strategy)

        return {
            "strategy_id": str(strategy.id),
            "total_nodes": nodes.count(),
            "total_edges": edges.count(),
            "nodes": [
                {
                    "id": n.id,
                    "type": n.node_type,
                    "label": n.label,
                    "properties": n.properties
                }
                for n in nodes
            ],
            "edges": [
                {
                    "id": str(e.id),
                    "source": e.source_id,
                    "target": e.target_id,
                    "type": e.edge_type,
                    "label": e.label
                }
                for e in edges
            ]
        }

    def _generate_path_narrative(
        self,
        scheme_node: EvidenceGraphNode,
        overall_status: str,
        fact_nodes: List[EvidenceGraphNode],
        rule_nodes: List[EvidenceGraphNode],
        evidence_nodes: List[EvidenceGraphNode],
        rel_nodes: List[EvidenceGraphNode],
        blocker_nodes: List[EvidenceGraphNode],
        action_nodes: List[EvidenceGraphNode]
    ) -> str:
        facts_summary = "; ".join([f.label for f in fact_nodes[:2]]) if fact_nodes else "Business profile facts"
        rules_summary = "; ".join([r.label for r in rule_nodes[:2]]) if rule_nodes else "Statutory conditions"
        ev_summary = evidence_nodes[0].label if evidence_nodes else "Official Gazette guidelines"

        if overall_status == "MATCH":
            narrative = (
                f"Your verified profile ({facts_summary}) fully satisfies statutory conditions ({rules_summary}) "
                f"under '{scheme_node.label}'. This evaluation is grounded in official policy evidence ({ev_summary}), "
                f"resulting in confirmed MATCH status."
            )
        elif overall_status == "DOES_NOT_MATCH":
            blocker_text = blocker_nodes[0].label if blocker_nodes else "Mandatory statutory criteria"
            narrative = (
                f"While your profile ({facts_summary}) was evaluated against '{scheme_node.label}', "
                f"a statutory blocker was triggered ({blocker_text}), making the enterprise ineligible for this specific scheme."
            )
        else:
            narrative = (
                f"Your profile facts ({facts_summary}) partially align with '{scheme_node.label}', but official verification "
                f"is required for key rules ({rules_summary}) per {ev_summary} before formal application."
            )

        if rel_nodes:
            narrative += f" Additionally, cross-scheme analysis indicates: {rel_nodes[0].label}."
        if action_nodes:
            narrative += f" Immediate recommended step: {action_nodes[0].label}."

        return narrative
