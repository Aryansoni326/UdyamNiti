/**
 * UdyamNiti Core Type Definitions
 * Complete domain types representing the MSME Decision Support Model.
 */

// ─── Status & Evidence Enums ──────────────────────────────────────────────────

export type MatchStatus =
  | 'MATCH'
  | 'POTENTIAL_MATCH'
  | 'UNKNOWN'
  | 'DOES_NOT_MATCH'
  | 'REQUIRES_OFFICIAL_VERIFICATION'

export type EvidenceSourceType =
  | 'self_declared'
  | 'document_supported'
  | 'official_source'
  | 'rule_matched'
  | 'ai_explanation'

export type MSMECategory = 'micro' | 'small' | 'medium'

export type ConditionStatus = 'PASS' | 'FAIL' | 'UNKNOWN'

export type ConditionImportance = 'mandatory' | 'preferred' | 'bonus' | 'info'

export type SupportType =
  | 'capital_subsidy'
  | 'interest_subvention'
  | 'collateral_free_credit'
  | 'market_development'
  | 'technology_adoption'
  | 'infrastructure_grant'
  | 'quality_certification'
  | 'export_incentive'

export type RelationshipType =
  | 'prerequisite_for'
  | 'stacks_with'
  | 'conflicts_with'
  | 'enhances'
  | 'alternative_to'

export type ActionCategory =
  | 'prerequisite'
  | 'apply_now'
  | 'resolve_unknowns'
  | 'information'

// ─── Business Profile ─────────────────────────────────────────────────────────

export interface BusinessProfile {
  id: string
  business_name: string
  udyam_registration_number?: string
  msme_category: MSMECategory
  entity_type: 'proprietorship' | 'partnership' | 'llp' | 'pvt_ltd' | 'public_ltd' | string
  industry_sector: string
  state: string
  district: string
  investment_in_plant_machinery_lakhs?: number
  annual_turnover_lakhs?: number
  is_women_owned: boolean
  is_sc_st_owned: boolean
  is_npa: boolean
  has_bank_account: boolean
  has_existing_loan: boolean
  years_in_operation?: number
  total_employees?: number
  created_at: string
  updated_at?: string
}

// ─── Business Goal ────────────────────────────────────────────────────────────

export interface BusinessGoal {
  id: string
  business_profile: string
  raw_goal_text: string
  parsed_objective: string
  parsed_project_type: string
  parsed_investment_amount_lakhs?: number
  parsed_support_categories: string[]
  parsed_missing_info: string[]
  status: 'pending' | 'analyzing' | 'ready' | 'error'
  created_at: string
}

// ─── Evidence & Citations ─────────────────────────────────────────────────────

export interface PolicyCitation {
  id?: string
  document_name: string
  document_type?: 'gazette_notification' | 'operational_guideline' | 'policy_circular' | 'scheme_faq'
  clause_or_section: string
  excerpt: string
  effective_date?: string
  last_verified_date?: string
  official_url: string
  version?: string
}

export interface ConditionResult {
  rule_name: string
  display_label: string
  status: ConditionStatus
  explanation: string
  importance: ConditionImportance
  source_clause: string
  citation?: PolicyCitation
  missing_field?: string
}

// ─── Scheme Opportunities ─────────────────────────────────────────────────────

export interface SchemeDocumentItem {
  id: string
  name: string
  desc: string
  category: string
  mandatory: boolean
}

export interface SchemeResult {
  id: string
  scheme_code: string
  name: string
  short_name: string
  ministry: string
  implementing_agency?: string
  level: 'central' | 'state' | 'state_gujarat' | string
  support_type: SupportType | string
  status?: MatchStatus | string
  score?: number
  max_benefit_lakhs?: number
  benefit_percentage?: number
  benefit_description: string
  description?: string
  eligibility_summary?: string
  application_process?: string
  application_steps?: string[]
  official_portal_url?: string
  gazette_notification?: string
  deadline?: string
  is_best_deal?: boolean
  best_deal_tag?: string
  best_deal_highlight?: string
  target_msme_categories?: string[]
  target_sectors?: string[]
  document_count?: number
  required_documents?: SchemeDocumentItem[]
  summary_explanation?: string
  mandatory_failures?: string[]
  missing_info?: string[]
  condition_results?: ConditionResult[]
  primary_citation?: PolicyCitation
  unlock_action?: string
  rules?: Array<{
    rule_name: string
    display_label: string
    importance: string
    source_clause: string
    source_document?: string
    failure_message?: string
  }>
  benefits?: Array<{
    benefit_name: string
    amount_or_percentage: string
    cap_amount_lakhs?: number
    conditions?: string
    source_clause?: string
  }>
}

// ─── Relationships & Graphs ───────────────────────────────────────────────────

export interface SchemeRelationship {
  id?: string
  type: RelationshipType
  scheme_a_name: string
  scheme_a_code: string
  scheme_b_name: string
  scheme_b_code: string
  description: string
  order_importance?: 'strict_first' | 'recommended_first' | 'concurrent'
}

// ─── Action Plan & Unlocks ────────────────────────────────────────────────────

export interface ActionItem {
  id?: string
  priority: number
  category: ActionCategory
  title: string
  description: string
  portal?: string | null
  portal_label?: string
  estimated_time: string
  blocker_for: string[]
  unlocks_scheme_code?: string
  potential_benefit_lakhs?: number
  status?: 'pending' | 'in_progress' | 'completed'
}

export interface UnlockRecommendation {
  id: string
  target_scheme_code: string
  target_scheme_name: string
  action_required: string
  missing_fact: string
  unlocked_benefit_lakhs?: number
  difficulty: 'low' | 'medium' | 'high'
  estimated_days: number
}

// ─── Strategy Document ────────────────────────────────────────────────────────

export interface Strategy {
  id: string
  goal: BusinessGoal
  business_profile: {
    id: string
    business_name: string
    msme_category: string
    industry_sector: string
    state: string
    district: string
    investment_lakhs?: number
    turnover_lakhs?: number
    udyam_number?: string
    is_women_owned: boolean
    is_sc_st_owned: boolean
    is_npa: boolean
  }
  narrative: string
  total_opportunities: number
  matched_count: number
  potential_count: number
  schemes: SchemeResult[]
  relationships: SchemeRelationship[]
  action_plan: ActionItem[]
  unlock_recommendations?: UnlockRecommendation[]
  created_at: string
}

// ─── Policy Impact & Monitoring ───────────────────────────────────────────────

export interface PolicyChange {
  id: string
  scheme_name: string
  scheme_code: string
  change_type: 'subsidy_revised' | 'eligibility_expanded' | 'deadline_extended' | 'budget_exhausted' | 'clause_updated' | string
  change_summary: string
  old_value?: Record<string, unknown>
  new_value?: Record<string, unknown>
  effective_date?: string
  source?: string
  official_url?: string
  detected_at: string
  impact_severity?: 'high' | 'medium' | 'low'
  affected_profiles_count?: number
}

// ─── Form Inputs ──────────────────────────────────────────────────────────────

export interface ProfileFormData {
  business_name: string
  udyam_registration_number?: string
  msme_category: MSMECategory
  entity_type: string
  industry_sector: string
  state: string
  district: string
  investment_in_plant_machinery_lakhs?: number
  annual_turnover_lakhs?: number
  is_women_owned: boolean
  is_sc_st_owned: boolean
  is_npa: boolean
  has_bank_account: boolean
  has_existing_loan: boolean
  years_in_operation?: number
  total_employees?: number
}

export interface GoalFormData {
  goal_text: string
  target_timeline_months?: number
}
