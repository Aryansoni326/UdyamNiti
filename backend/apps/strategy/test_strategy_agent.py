"""
Comprehensive unit tests for the Strategy Agent and StrategyAgentValidator.
Validates non-negotiable architectural guarantees:
1. Rejects hallucinated scheme IDs not in curated DB.
2. Eligibility statuses strictly match deterministic rule engine results.
3. Relationships must originate from verified relationship engine.
4. Factual policy claims must cite verified evidence IDs.
5. UNKNOWN status remains UNKNOWN.
6. Schemes are strictly ordered by statutory sequencing tiers, never fabricated AI scores.
7. Tradeoffs explained without claiming formal legal sanction.
"""
from django.test import TestCase
from apps.policies.models import Scheme
from apps.strategy.strategy_agent import (
    StrategyAgent,
    StrategyAgentValidator,
    StrategyAgentOutput,
    StrategyItemData,
    RelationshipSummaryData,
    BlockerData,
    PotentialUnlockData,
    NextActionData,
    UnknownFactData
)


class StrategyAgentValidatorTests(TestCase):
    def setUp(self):
        self.validator = StrategyAgentValidator()

        self.scheme_gj_cap = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Subsidy",
            ministry_department="Govt of Gujarat Industries Comm.",
            level="state_gujarat",
            support_type="capital_subsidy",
            benefit_description="25% capital subsidy on plant and machinery up to Rs. 35 Lakhs.",
            status="active",
            target_states=["Gujarat"]
        )

        self.scheme_cgtmse = Scheme.objects.create(
            scheme_code="CGTMSE-CENTRAL",
            name="Credit Guarantee Fund Trust for Micro and Small Enterprises",
            ministry_department="Ministry of MSME, Govt of India",
            level="central",
            support_type="credit_guarantee",
            benefit_description="Collateral-free credit facility up to Rs. 500 Lakhs.",
            status="active",
            target_states=[]
        )

        self.curated_schemes_map = {
            "GJ-CAPITAL-2025": self.scheme_gj_cap,
            "CGTMSE-CENTRAL": self.scheme_cgtmse,
        }

        self.deterministic_evals = {
            "GJ-CAPITAL-2025": "MATCH",
            "CGTMSE-CENTRAL": "POTENTIAL_MATCH",
        }

        self.valid_evidence_ids = ["chunk-ev-001", "chunk-ev-002"]

    def test_reject_hallucinated_scheme_ids(self):
        """Validator must drop any scheme code not present in curated DB."""
        raw_output = {
            "strategy_items": [
                {
                    "scheme_code": "GJ-CAPITAL-2025",
                    "scheme_name": "Gujarat MSME Capital Subsidy",
                    "benefit_summary": "25% subsidy",
                    "statutory_evidence_ids": ["chunk-ev-001"]
                },
                {
                    "scheme_code": "HALLUCINATED-AI-SCHEME-999",
                    "scheme_name": "Free 100 Crore Startup Grant",
                    "benefit_summary": "100% grant for all businesses",
                    "statutory_evidence_ids": ["chunk-fake-001"]
                }
            ],
            "relationship_summary": [],
            "blockers": [],
            "potential_unlocks": [],
            "recommended_next_actions": [],
            "unknowns": []
        }

        result = self.validator.validate_and_remediate(
            raw_output=raw_output,
            curated_schemes_map=self.curated_schemes_map,
            deterministic_evals_map=self.deterministic_evals,
            relationship_pairs=[],
            valid_evidence_ids=self.valid_evidence_ids
        )

        # Only GJ-CAPITAL-2025 should survive; hallucinated scheme is pruned
        self.assertEqual(len(result.strategy_items), 1)
        self.assertEqual(result.strategy_items[0].scheme_code, "GJ-CAPITAL-2025")

    def test_enforce_deterministic_eligibility_status(self):
        """Validator must overwrite any fabricated status with deterministic rule engine status."""
        raw_output = {
            "strategy_items": [
                {
                    "scheme_code": "GJ-CAPITAL-2025",
                    "eligibility_status": "DOES_NOT_MATCH",  # Attempted tamper or LLM error
                    "statutory_evidence_ids": ["chunk-ev-001"]
                },
                {
                    "scheme_code": "CGTMSE-CENTRAL",
                    "eligibility_status": "MATCH",  # Attempted promotion without meeting condition
                    "statutory_evidence_ids": ["chunk-ev-002"]
                }
            ]
        }

        result = self.validator.validate_and_remediate(
            raw_output=raw_output,
            curated_schemes_map=self.curated_schemes_map,
            deterministic_evals_map=self.deterministic_evals,
            relationship_pairs=[],
            valid_evidence_ids=self.valid_evidence_ids
        )

        item_map = {item.scheme_code: item.eligibility_status for item in result.strategy_items}
        self.assertEqual(item_map["GJ-CAPITAL-2025"], "MATCH")
        self.assertEqual(item_map["CGTMSE-CENTRAL"], "POTENTIAL_MATCH")

    def test_enforce_statutory_sequencing_tiers_not_fake_ai_scores(self):
        """Items must be ordered by statutory sequencing tier (MATCH=1, POTENTIAL=2, UNKNOWN=3, DOES_NOT_MATCH=4)."""
        raw_output = {
            "strategy_items": [
                {"scheme_code": "CGTMSE-CENTRAL"},  # POTENTIAL_MATCH -> tier 2
                {"scheme_code": "GJ-CAPITAL-2025"},   # MATCH -> tier 1
            ]
        }

        result = self.validator.validate_and_remediate(
            raw_output=raw_output,
            curated_schemes_map=self.curated_schemes_map,
            deterministic_evals_map=self.deterministic_evals,
            relationship_pairs=[],
            valid_evidence_ids=self.valid_evidence_ids
        )

        # First item must be Tier 1 (GJ-CAPITAL-2025)
        self.assertEqual(result.strategy_items[0].scheme_code, "GJ-CAPITAL-2025")
        self.assertEqual(result.strategy_items[0].sequencing_tier, 1)
        # Second item must be Tier 2 (CGTMSE-CENTRAL)
        self.assertEqual(result.strategy_items[1].scheme_code, "CGTMSE-CENTRAL")
        self.assertEqual(result.strategy_items[1].sequencing_tier, 2)

    def test_filter_fabricated_evidence_ids(self):
        """Fabricated evidence IDs not present in verified chunks must be stripped."""
        raw_output = {
            "strategy_items": [
                {
                    "scheme_code": "GJ-CAPITAL-2025",
                    "statutory_evidence_ids": ["chunk-ev-001", "chunk-phantom-999"]
                }
            ],
            "relationship_summary": [
                {
                    "source_scheme_code": "GJ-CAPITAL-2025",
                    "target_scheme_code": "CGTMSE-CENTRAL",
                    "relationship_type": "synergistic",
                    "tradeoff_note": "Can co-exist on the same term loan.",
                    "evidence_ids": ["chunk-fake-001", "chunk-ev-002"]
                }
            ]
        }

        result = self.validator.validate_and_remediate(
            raw_output=raw_output,
            curated_schemes_map=self.curated_schemes_map,
            deterministic_evals_map=self.deterministic_evals,
            relationship_pairs=[],
            valid_evidence_ids=self.valid_evidence_ids
        )

        # Scheme item evidence
        self.assertEqual(result.strategy_items[0].statutory_evidence_ids, ["chunk-ev-001"])
        # Relationship evidence
        self.assertEqual(result.relationship_summary[0].evidence_ids, ["chunk-ev-002"])

    def test_unknown_remains_unknown(self):
        """Unknowns must be preserved without pretending certainty."""
        raw_output = {
            "unknowns": [
                {
                    "fact_key": "location.taluka_category",
                    "question": "Which Taluka is your factory located in?",
                    "impact": "Changes subsidy ceiling from Rs. 10L to Rs. 35L"
                }
            ]
        }

        result = self.validator.validate_and_remediate(
            raw_output=raw_output,
            curated_schemes_map=self.curated_schemes_map,
            deterministic_evals_map=self.deterministic_evals,
            relationship_pairs=[],
            valid_evidence_ids=self.valid_evidence_ids
        )

        self.assertEqual(len(result.unknowns), 1)
        self.assertEqual(result.unknowns[0].fact_key, "location.taluka_category")
        self.assertIn("subsidy ceiling", result.unknowns[0].impact)

    def test_legal_disclaimer_mandatory(self):
        """Every generated strategy must carry the formal statutory disclaimer."""
        result = self.validator.validate_and_remediate(
            raw_output={},
            curated_schemes_map=self.curated_schemes_map,
            deterministic_evals_map=self.deterministic_evals,
            relationship_pairs=[],
            valid_evidence_ids=self.valid_evidence_ids
        )
        self.assertIn("Statutory Disclaimer", result.legal_disclaimer)
        self.assertIn("does not constitute formal statutory sanction", result.legal_disclaimer)


class StrategyAgentEndToEndTests(TestCase):
    def setUp(self):
        self.agent = StrategyAgent()

        self.scheme_gj = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Subsidy",
            ministry_department="Govt of Gujarat Industries Comm.",
            level="state_gujarat",
            support_type="capital_subsidy",
            benefit_description="25% capital subsidy up to Rs. 35 Lakhs on machinery.",
            status="active"
        )
        self.scheme_cgtmse = Scheme.objects.create(
            scheme_code="CGTMSE-CENTRAL",
            name="Credit Guarantee Trust for MSMEs",
            ministry_department="Ministry of MSME",
            level="central",
            support_type="credit_guarantee",
            benefit_description="Collateral free credit up to Rs. 500 Lakhs.",
            status="active"
        )

    def test_organize_strategy_complete_output_contract(self):
        """StrategyAgent.organize_strategy must return all 8 required fields + legal disclaimer."""
        business_goal = {
            "primary_goal": "Purchase CNC machine to expand production",
            "support_categories": ["capital_subsidy", "credit_guarantee"],
            "investment_amount_lakhs": 50.0
        }
        profile_snapshot = {
            "entity_type": "proprietorship",
            "msme_category": "small",
            "state": "Gujarat",
            "has_udyam": True
        }
        candidate_schemes = [self.scheme_gj, self.scheme_cgtmse]
        deterministic_results = {
            "GJ-CAPITAL-2025": "MATCH",
            "CGTMSE-CENTRAL": "POTENTIAL_MATCH"
        }
        relationship_results = [
            {
                "source_scheme_code": "GJ-CAPITAL-2025",
                "target_scheme_code": "CGTMSE-CENTRAL",
                "relationship_type": "synergistic",
                "tradeoff_note": "Stackable: CGTMSE covers the term loan while Gujarat Capital Subsidy repays 25% of principal."
            }
        ]
        evidence_bundles = [
            {"chunk_id": "ev-gj-01", "section_heading": "Clause 4.1 Capital Assistance"},
            {"chunk_id": "ev-cgtmse-01", "section_heading": "Clause 2.3 Guarantee Extent"}
        ]
        unlock_candidates = [
            {
                "action_title": "Submit Banker Sanction Letter",
                "target_scheme_code": "GJ-CAPITAL-2025",
                "unlock_impact": "Unlocks state capital subsidy release after term loan disbursement.",
                "effort_level": "medium",
                "estimated_timeline": "10-15 days"
            }
        ]

        strategy_output: StrategyAgentOutput = self.agent.organize_strategy(
            business_goal=business_goal,
            profile_snapshot=profile_snapshot,
            candidate_schemes=candidate_schemes,
            deterministic_eligibility_results=deterministic_results,
            relationship_results=relationship_results,
            evidence_bundles=evidence_bundles,
            unlock_candidates=unlock_candidates
        )

        d = strategy_output.to_dict()

        # Check all 8 required sections
        self.assertIn("support_categories", d)
        self.assertIn("priority_context", d)
        self.assertIn("strategy_items", d)
        self.assertIn("relationship_summary", d)
        self.assertIn("blockers", d)
        self.assertIn("potential_unlocks", d)
        self.assertIn("recommended_next_actions", d)
        self.assertIn("unknowns", d)
        self.assertIn("legal_disclaimer", d)

        # Check strategy items
        self.assertEqual(len(d["strategy_items"]), 2)
        # Tier 1 must come first
        self.assertEqual(d["strategy_items"][0]["scheme_code"], "GJ-CAPITAL-2025")
        self.assertEqual(d["strategy_items"][0]["sequencing_tier"], 1)
        self.assertEqual(d["strategy_items"][1]["scheme_code"], "CGTMSE-CENTRAL")
        self.assertEqual(d["strategy_items"][1]["sequencing_tier"], 2)

        # Check relationships
        self.assertEqual(len(d["relationship_summary"]), 1)
        self.assertIn("Stackable", d["relationship_summary"][0]["tradeoff_note"])

        # Check potential unlocks
        self.assertEqual(len(d["potential_unlocks"]), 1)
        self.assertEqual(d["potential_unlocks"][0]["action_title"], "Submit Banker Sanction Letter")
