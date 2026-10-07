"""
Gemini-powered agents for UdyamNiti.

Goal Agent: Parses natural language business goals into structured intent.
Strategy Agent: Assembles opportunity landscape into coherent strategy narrative.
"""
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def _get_gemini_client():
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai.GenerativeModel(settings.GEMINI_MODEL)
    except Exception as e:
        logger.warning(f"Gemini client init failed: {e}")
        return None


GOAL_PARSE_PROMPT = """You are an expert MSME policy analyst. Parse the following business goal into structured JSON.

Business Goal: "{goal_text}"

Extract and return a JSON object with these fields:
{{
  "objective": "Clear one-sentence objective",
  "project_type": "One of: machinery_purchase, working_capital, export_expansion, technology_upgrade, new_unit, quality_certification, market_expansion, skill_development, infrastructure, other",
  "investment_amount_lakhs": <number or null>,
  "support_categories": ["list of relevant: capital_subsidy, interest_subvention, credit_guarantee, technology, export, marketing, skill, quality, digital, infrastructure"],
  "industry_hints": ["relevant industry sectors, e.g. manufacturing, engineering, textiles"],
  "missing_high_impact_info": ["list of critical business facts that would unlock more schemes, e.g. 'Annual turnover to confirm MSME category', 'SC/ST ownership status for additional subsidies'"],
  "rag_queries": ["2-3 specific policy search queries to find relevant schemes"]
}}

Return ONLY valid JSON, no explanation."""


STRATEGY_PROMPT = """You are UdyamNiti, an expert MSME government-support strategist.

MSME Profile:
{profile_summary}

Business Goal:
{goal_text}

Eligible/Potential Schemes Found:
{schemes_summary}

Cross-scheme Relationships:
{relationships}

Write a coherent government-support strategy narrative (3-4 paragraphs) that:
1. Acknowledges the specific business goal
2. Highlights the primary recommended scheme and why it fits
3. Mentions complementary schemes and synergies
4. Notes any important prerequisites or sequencing
5. Gives a concrete next step

Be specific, professional, and cite scheme names. Reference official portals where relevant.
Write in second person ("Your business..."). Keep under 300 words."""


class GoalAgent:
    """Parses natural language business goals into structured intent using Gemini."""

    def __init__(self):
        self.model = _get_gemini_client()

    def parse(self, goal_text: str) -> dict:
        """Parse goal text into structured intent. Falls back to mock if Gemini unavailable."""
        if not self.model or not settings.GEMINI_API_KEY:
            return self._mock_parse(goal_text)

        prompt = GOAL_PARSE_PROMPT.format(goal_text=goal_text)
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # Strip markdown code fences if present
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            return json.loads(text)
        except Exception as e:
            logger.error(f"GoalAgent parse error: {e}")
            return self._mock_parse(goal_text)

    def _mock_parse(self, goal_text: str) -> dict:
        """Deterministic mock for demo/dev when Gemini is unavailable."""
        goal_lower = goal_text.lower()
        categories = []
        project_type = 'other'
        investment = None

        if any(w in goal_lower for w in ['machine', 'machinery', 'cnc', 'equipment', 'plant']):
            categories.extend(['capital_subsidy', 'credit_guarantee', 'technology'])
            project_type = 'machinery_purchase'

        if any(w in goal_lower for w in ['export', 'international', 'overseas']):
            categories.append('export')
            project_type = 'export_expansion'

        if any(w in goal_lower for w in ['digital', 'software', 'erp', 'technology']):
            categories.append('digital')

        # Extract amount
        import re
        m = re.search(r'₹?\s*([\d,]+)\s*(lakh|crore|cr)', goal_lower)
        if m:
            amount = float(m.group(1).replace(',', ''))
            if 'crore' in m.group(2) or 'cr' in m.group(2):
                amount *= 100
            investment = amount

        return {
            'objective': f"Achieve: {goal_text[:100]}",
            'project_type': project_type,
            'investment_amount_lakhs': investment,
            'support_categories': list(set(categories)) or ['capital_subsidy', 'credit_guarantee'],
            'industry_hints': ['manufacturing', 'engineering'],
            'missing_high_impact_info': [
                'Annual turnover (last financial year) — determines MSME category and scheme limits',
                'SC/ST or women ownership — qualifies for additional benefits',
                'Existing bank loan details — needed for credit guarantee schemes',
            ],
            'rag_queries': [
                f"MSME capital subsidy machinery purchase scheme',",
                f"credit guarantee loan MSME equipment Gujarat",
                f"technology upgrade fund small enterprise",
            ]
        }


class StrategyAgent:
    """Assembles eligibility results into a coherent strategy narrative."""

    def __init__(self):
        self.model = _get_gemini_client()

    def generate_narrative(
        self,
        profile,
        goal_text: str,
        eligible_schemes: list,
        relationships: list,
    ) -> str:
        if not self.model or not settings.GEMINI_API_KEY:
            return self._mock_narrative(profile, eligible_schemes)

        profile_summary = (
            f"Business: {profile.business_name}, {profile.msme_category.title()} MSME, "
            f"{profile.industry_sector} in {profile.district}, {profile.state}. "
            f"Investment: ₹{profile.investment_in_plant_machinery_lakhs} L, "
            f"Turnover: ₹{profile.annual_turnover_lakhs} L"
        )
        schemes_summary = "\n".join([
            f"- {s['name']} ({s['status']}): {s.get('benefit', 'N/A')}"
            for s in eligible_schemes[:10]
        ])
        rel_summary = "\n".join([
            f"- {r['type']}: {r['scheme_a']} ↔ {r['scheme_b']}"
            for r in relationships[:5]
        ]) or "No cross-scheme relationships identified."

        prompt = STRATEGY_PROMPT.format(
            profile_summary=profile_summary,
            goal_text=goal_text,
            schemes_summary=schemes_summary,
            relationships=rel_summary,
        )

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"StrategyAgent error: {e}")
            return self._mock_narrative(profile, eligible_schemes)

    def _mock_narrative(self, profile, eligible_schemes):
        top_schemes = eligible_schemes[:3]
        names = [s['name'] for s in top_schemes]
        return (
            f"Your business, {profile.business_name}, has a strong pathway to government support "
            f"for this capital investment goal. Based on your profile as a {profile.msme_category} MSME "
            f"in {profile.state}, we have identified {len(eligible_schemes)} relevant programs.\n\n"
            f"The primary recommendation is the **{names[0] if names else 'CLCSS'}**, which directly "
            f"addresses machinery acquisition with capital subsidy support. "
            f"This should be your first application target.\n\n"
            f"Complementary schemes like {', '.join(names[1:3]) if len(names) > 1 else 'CGTMSE'} can "
            f"be pursued in parallel to stack benefits and reduce financial risk. "
            f"Note that credit guarantee schemes require a formal loan application first — "
            f"coordinate with your bank early.\n\n"
            f"**Immediate next step**: Register on the Udyam portal if not already done, "
            f"then visit the official scheme portal to initiate your application."
        )
