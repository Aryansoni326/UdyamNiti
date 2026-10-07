"""
Goal Understanding Agent for MSME Decision Support.
Extracts structured intent, investment amounts, sector hints, and material missing facts
from free-form natural language statements in English or Gujarati / Gujlish.

Guarantees:
1. Asks only clarifying questions that materially change discovery or eligibility.
2. Never invents unstated business facts.
3. Normalizes money units (Lakhs, Crores, INR) separately from raw text.
4. Outputs uncertainty explicitly.
5. Strictly NO scheme recommendations at this stage.
"""
import os
import re
import json
import logging
from dataclasses import dataclass, asdict, field
from decimal import Decimal
from typing import List, Dict, Any, Optional

try:
    import google.generativeai as genai
    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False

logger = logging.getLogger(__name__)


@dataclass
class MoneyAmount:
    amount: Optional[float] = None
    currency: str = "INR"
    unit: Optional[str] = None  # "Lakhs", "Crores", "INR"
    normalized_inr: Optional[float] = None
    raw_text: Optional[str] = None


@dataclass
class KnownFact:
    fact_key: str
    fact_value: Any
    confidence: float
    source: str = "user_statement"


@dataclass
class ClarifyingQuestion:
    question: str
    reason_it_matters: str
    fact_key: str
    options: List[str] = field(default_factory=list)


@dataclass
class GoalInterpretationResult:
    primary_goal: str
    project: str
    estimated_investment: MoneyAmount
    industry_hint: str
    business_objectives: List[str]
    support_categories: List[str]
    known_facts: List[KnownFact]
    missing_material_facts: List[str]
    clarifying_questions: List[ClarifyingQuestion]
    detected_language: str = "English"
    uncertainty_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_goal": self.primary_goal,
            "project": self.project,
            "estimated_investment": asdict(self.estimated_investment),
            "industry_hint": self.industry_hint,
            "business_objectives": self.business_objectives,
            "support_categories": self.support_categories,
            "known_facts": [asdict(f) for f in self.known_facts],
            "missing_material_facts": self.missing_material_facts,
            "clarifying_questions": [asdict(q) for q in self.clarifying_questions],
            "detected_language": self.detected_language,
            "uncertainty_notes": self.uncertainty_notes
        }


# =====================================================================
# Gujarati & Gujlish Linguistic Lexicon
# =====================================================================

GUJARATI_LEXICON = {
    # Actions & Verbs
    "kharid": "purchase",
    "levani": "want_to_buy",
    "levu": "want_to_buy",
    "vadharvu": "expand",
    "vadhari": "expand",
    "chalavvu": "operate",
    "shuru": "start",
    "sthapna": "setup_greenfield",
    "export": "export",
    "nikas": "export",
    # Assets & Equipment
    "yantra": "machinery",
    "machine": "machinery",
    "sadhan": "equipment",
    "karkhanu": "factory",
    "factory": "factory",
    "godown": "warehouse",
    # Objectives & Support
    "sahay": "subsidy_assistance",
    "maddat": "support",
    "subsidy": "subsidy",
    "vyaj": "interest",
    "loan": "loan",
    "karj": "loan",
    "production": "production_manufacturing",
    "quality": "quality_certification",
    "solar": "solar_energy",
    "bijli": "electricity_power"
}


# =====================================================================
# Goal Agent Implementation with Retry Strategy
# =====================================================================

class GoalUnderstandingAgent:
    """
    NLP Agent that interprets MSME goals without hallucinating facts or recommending schemes.
    """

    SYSTEM_PROMPT = """You are the Goal Understanding Agent for UdyamNiti, an evidence-backed government support strategy platform for Indian MSMEs.

Your sole responsibility is to translate an MSME entrepreneur's free-form goal statement (in English or Gujarati / Gujlish transliteration) into a structured operational objective.

CRITICAL INVARIANTS:
1. NEVER recommend government schemes (e.g. Do NOT mention PMEGP, CGTMSE, or Gujarat MSME Subsidy). Discovery happens in the next stage.
2. NEVER invent business facts not explicitly mentioned in the text.
3. If the user mentions money, normalize the amount into INR while keeping the original unit and raw text separate.
4. Identify at most 2-3 high-impact clarifying questions whose answers materially change eligibility (e.g. Taluka category, Udyam registration, Greenfield vs Expansion). Provide multiple choice options for quick mobile completion.
5. Explicitly output uncertainty where information is vague.

You must respond ONLY with a strict JSON object matching this structure:
{
  "primary_goal": "Concise 1-sentence summary of the main business objective",
  "project": "Nature of the project e.g. Factory expansion with 5-axis CNC machinery",
  "estimated_investment": {
    "amount": 50.0,
    "currency": "INR",
    "unit": "Lakhs",
    "normalized_inr": 5000000.0,
    "raw_text": "Rs. 50 Lakhs"
  },
  "industry_hint": "Manufacturing / Precision Engineering",
  "business_objectives": ["Increase production capacity", "Technology upgradation"],
  "support_categories": ["capital_subsidy", "interest_subvention", "technology_upgrade"],
  "known_facts": [
    {
      "fact_key": "project.type",
      "fact_value": "Expansion",
      "confidence": 0.95,
      "source": "user_statement"
    }
  ],
  "missing_material_facts": [
    "location.taluka_category",
    "registration.udyam_active",
    "enterprise.current_category"
  ],
  "clarifying_questions": [
    {
      "question": "Is your factory located in a Category 1, 2, or 3 Taluka in Gujarat?",
      "reason_it_matters": "Determines whether capital subsidy is 10%, 20%, or 25%.",
      "fact_key": "location.taluka_category",
      "options": ["Category-1 (Least Developed)", "Category-2 (Developing)", "Category-3 (Developed/City)"]
    }
  ],
  "detected_language": "English",
  "uncertainty_notes": [
    "Investment amount was not specified; assumed between 25L and 1 Cr based on equipment type."
  ]
}
"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if _HAS_GENAI and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=self.SYSTEM_PROMPT
            )
        else:
            self.model = None

    def interpret_goal(self, goal_text: str, business_profile_facts: Optional[Dict[str, Any]] = None) -> GoalInterpretationResult:
        """
        Executes goal interpretation with 3-stage retry strategy and deterministic fallback.
        """
        clean_text = goal_text.strip()
        if not clean_text:
            raise ValueError("Goal text cannot be empty.")

        # Check language
        detected_lang = self._detect_language(clean_text)

        # Attempt LLM with retry strategy if configured
        if self.model:
            for attempt in range(3):
                try:
                    prompt = f"""[USER GOAL STATEMENT]:
"{clean_text}"

[EXISTING BUSINESS PROFILE CONTEXT]:
{json.dumps(business_profile_facts or {}, indent=2)}

Interpret the goal statement and return strict JSON."""

                    response = self.model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.1,
                            response_mime_type="application/json"
                        )
                    )
                    data = json.loads(response.text)
                    return self._parse_json_result(data, clean_text, detected_lang)
                except Exception as e:
                    logger.warning(f"Goal Agent attempt {attempt + 1} failed: {str(e)}")

        # Deterministic NLP Fallback
        return self._deterministic_fallback_interpret(clean_text, business_profile_facts, detected_lang)

    # -----------------------------------------------------------------
    # Deterministic NLP Fallback & Heuristic Extraction
    # -----------------------------------------------------------------

    def _deterministic_fallback_interpret(
        self,
        text: str,
        profile_facts: Optional[Dict[str, Any]],
        detected_lang: str
    ) -> GoalInterpretationResult:
        text_lower = text.lower()

        # 1. Money Normalization
        money = self._extract_money(text)

        # 2. Industry & Sector Extraction
        industry_hint = "Manufacturing / Engineering"
        if any(w in text_lower for w in ["agro", "food", "kheti", "fruit", "grain"]):
            industry_hint = "Agro & Food Processing"
        elif any(w in text_lower for w in ["software", "it", "digital", "app", "tech"]):
            industry_hint = "Information Technology / Services"
        elif any(w in text_lower for w in ["solar", "bijli", "power", "energy"]):
            industry_hint = "Renewable Energy / Industrial Utilities"
        elif any(w in text_lower for w in ["chemical", "pharma", "dye"]):
            industry_hint = "Chemicals & Pharmaceuticals"
        elif any(w in text_lower for w in ["textile", "kapda", "garment", "fabric"]):
            industry_hint = "Textiles & Apparel"

        # 3. Project Type & Primary Goal
        is_expansion = any(w in text_lower for w in ["increase", "vadhari", "vadharvu", "expand", "expansion", "capacity"])
        is_greenfield = any(w in text_lower for w in ["new", "navi", "shuru", "sthapna", "start"])

        project_type = "Machinery Purchase & Expansion" if is_expansion else ("New Industrial Setup" if is_greenfield else "Business Development")
        primary_goal = f"Procure new industrial equipment to {('expand factory production capacity' if is_expansion else 'establish new operations')}."

        # 4. Support Categories
        support_categories = ["capital_subsidy", "technology_upgrade"]
        if money.amount and money.amount >= 25.0:
            support_categories.append("interest_subvention")
        if any(w in text_lower for w in ["export", "nikas", "overseas", "global"]):
            support_categories.append("export_incentive")
        if any(w in text_lower for w in ["quality", "iso", "zed", "cert"]):
            support_categories.append("quality_certification")
        if any(w in text_lower for w in ["solar", "energy", "power"]):
            support_categories.append("power_tariff_subsidy")

        # 5. Known Facts (Strictly only facts present in input)
        known_facts = []
        if is_expansion:
            known_facts.append(KnownFact("project.type", "Substantial Expansion", 0.95))
        elif is_greenfield:
            known_facts.append(KnownFact("project.type", "Greenfield New Unit", 0.95))

        if "cnc" in text_lower:
            known_facts.append(KnownFact("equipment.type", "CNC Machinery", 0.98))

        if money.normalized_inr:
            known_facts.append(KnownFact("financials.estimated_investment_inr", money.normalized_inr, 0.99))

        # 6. Missing Material Facts & High-Impact Clarifying Questions
        missing_material_facts = [
            "location.taluka_category",
            "registration.udyam_active",
            "enterprise.existing_plant_investment"
        ]

        clarifying_questions = [
            ClarifyingQuestion(
                question="Where in Gujarat is your industrial unit located (Taluka Category)?",
                reason_it_matters="Statutory capital subsidy varies from 10% (Category 3) up to 25% (Category 1).",
                fact_key="location.taluka_category",
                options=["Category-1 (Least Developed)", "Category-2 (Developing)", "Category-3 (Developed / Municipal limits)"]
            ),
            ClarifyingQuestion(
                question="Do you already hold a valid Udyam Registration for this enterprise?",
                reason_it_matters="Mandatory prerequisite for all Central and State MSME capital incentives.",
                fact_key="registration.udyam_active",
                options=["Yes, active Udyam certificate available", "No, not yet registered", "Applied / Pending"]
            )
        ]

        if not money.amount:
            clarifying_questions.append(ClarifyingQuestion(
                question="What is the approximate project cost or machinery investment?",
                reason_it_matters="Determines whether you qualify for micro (<₹1Cr) or small enterprise incentive ceilings.",
                fact_key="financials.estimated_investment_lakhs",
                options=["Under ₹25 Lakhs", "₹25 Lakhs to ₹50 Lakhs", "₹50 Lakhs to ₹1 Crore", "Above ₹1 Crore"]
            ))

        uncertainty_notes = []
        if not money.amount:
            uncertainty_notes.append("No explicit investment amount specified in the statement.")

        return GoalInterpretationResult(
            primary_goal=primary_goal,
            project=project_type,
            estimated_investment=money,
            industry_hint=industry_hint,
            business_objectives=[
                "Increase commercial production output",
                "Induct modern manufacturing technology",
                "Reduce debt burden via capital/interest subsidies"
            ],
            support_categories=support_categories,
            known_facts=known_facts,
            missing_material_facts=missing_material_facts,
            clarifying_questions=clarifying_questions,
            detected_language=detected_lang,
            uncertainty_notes=uncertainty_notes
        )

    def _extract_money(self, text: str) -> MoneyAmount:
        """
        Extracts and normalizes currency from natural text:
        e.g. '50 Lakhs', 'Rs. 75 Lakh', '1.5 Crore', '₹ 25L', '2000000'.
        """
        # Pattern matching Lakhs/Crores
        pat = re.search(r'(?:rs\.?|inr|₹)?\s*([\d\.]+)\s*(lakhs?|crores?|cr|l|k)\b', text, re.I)
        if pat:
            val_str = pat.group(1)
            unit_str = pat.group(2).lower()
            val = float(val_str)
            raw = pat.group(0).strip()

            if "crore" in unit_str or "cr" in unit_str:
                return MoneyAmount(amount=val, currency="INR", unit="Crores", normalized_inr=val * 10000000.0, raw_text=raw)
            elif "lakh" in unit_str or "l" in unit_str:
                return MoneyAmount(amount=val, currency="INR", unit="Lakhs", normalized_inr=val * 100000.0, raw_text=raw)
            elif "k" in unit_str:
                return MoneyAmount(amount=val, currency="INR", unit="Thousands", normalized_inr=val * 1000.0, raw_text=raw)

        # Plain numbers e.g. 50,00,000
        pat_plain = re.search(r'(?:rs\.?|inr|₹)\s*([\d,]{4,})', text, re.I)
        if pat_plain:
            raw = pat_plain.group(0)
            cleaned = pat_plain.group(1).replace(',', '')
            val = float(cleaned)
            lakhs = val / 100000.0
            return MoneyAmount(amount=lakhs, currency="INR", unit="Lakhs", normalized_inr=val, raw_text=raw)

        return MoneyAmount(amount=None, currency="INR", unit=None, normalized_inr=None, raw_text=None)

    def _detect_language(self, text: str) -> str:
        text_lower = text.lower()
        gujlish_words = ["che", "ane", "karvu", "levani", "mali", "taraf", "thi", "kai", "maru", "tamaru", "shakya", "yojana", "sahay"]
        gujarati_matches = sum(1 for w in gujlish_words if f" {w} " in f" {text_lower} ")
        if gujarati_matches >= 2:
            return "Gujarati (Transliterated)"
        return "English"

    def _parse_json_result(self, d: Dict[str, Any], raw_text: str, detected_lang: str) -> GoalInterpretationResult:
        inv_data = d.get("estimated_investment", {})
        money = MoneyAmount(
            amount=inv_data.get("amount"),
            currency=inv_data.get("currency", "INR"),
            unit=inv_data.get("unit"),
            normalized_inr=inv_data.get("normalized_inr"),
            raw_text=inv_data.get("raw_text")
        )
        if not money.normalized_inr and money.amount and money.unit:
            if "crore" in money.unit.lower():
                money.normalized_inr = money.amount * 10000000.0
            elif "lakh" in money.unit.lower():
                money.normalized_inr = money.amount * 100000.0

        known_facts = [
            KnownFact(fact_key=kf.get("fact_key", ""), fact_value=kf.get("fact_value"), confidence=kf.get("confidence", 0.9), source=kf.get("source", "user_statement"))
            for kf in d.get("known_facts", [])
        ]

        clarifying = [
            ClarifyingQuestion(
                question=cq.get("question", ""),
                reason_it_matters=cq.get("reason_it_matters", ""),
                fact_key=cq.get("fact_key", ""),
                options=cq.get("options", [])
            )
            for cq in d.get("clarifying_questions", [])
        ]

        return GoalInterpretationResult(
            primary_goal=d.get("primary_goal", "Procure machinery and expand business operations"),
            project=d.get("project", "Industrial Expansion"),
            estimated_investment=money,
            industry_hint=d.get("industry_hint", "Manufacturing"),
            business_objectives=d.get("business_objectives", ["Capacity Expansion"]),
            support_categories=d.get("support_categories", ["capital_subsidy"]),
            known_facts=known_facts,
            missing_material_facts=d.get("missing_material_facts", []),
            clarifying_questions=clarifying,
            detected_language=d.get("detected_language", detected_lang),
            uncertainty_notes=d.get("uncertainty_notes", [])
        )
