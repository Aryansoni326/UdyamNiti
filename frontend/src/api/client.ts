import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken') || '',
  },
})

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null
  return null
}

// Interfaces
export interface BusinessProfile {
  id: string
  business_name: string
  udyam_registration_number?: string
  msme_category: 'micro' | 'small' | 'medium'
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
  created_at: string
}

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

export interface ConditionResult {
  rule_name: string
  display_label: string
  status: 'PASS' | 'FAIL' | 'UNKNOWN'
  explanation: string
  importance: 'mandatory' | 'preferred' | 'bonus' | 'info'
  source_clause: string
}

export interface SchemeResult {
  id: string
  scheme_code: string
  name: string
  short_name: string
  ministry: string
  level: 'central' | 'state' | 'state_gujarat'
  support_type: string
  status: 'MATCH' | 'POTENTIAL_MATCH' | 'DOES_NOT_MATCH' | 'UNKNOWN'
  score: number
  max_benefit_lakhs?: number
  benefit_percentage?: number
  benefit_description: string
  description: string
  eligibility_summary: string
  application_process: string
  official_portal_url: string
  summary_explanation: string
  mandatory_failures: string[]
  missing_info: string[]
  condition_results: ConditionResult[]
}

export interface Relationship {
  type: string
  scheme_a_name: string
  scheme_a_code: string
  scheme_b_name: string
  scheme_b_code: string
  description: string
}

export interface ActionItem {
  priority: number
  category: 'prerequisite' | 'apply_now' | 'resolve_unknowns' | 'information'
  title: string
  description: string
  portal?: string | null
  estimated_time: string
  blocker_for: string[]
}

export interface Strategy {
  id: string
  correlation_id?: string
  trace_id?: string
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
  relationships: Relationship[]
  action_plan: ActionItem[]
  created_at: string
}

export interface PolicyChange {
  id: string
  scheme_name: string
  scheme_code: string
  change_type: string
  change_summary: string
  old_value?: Record<string, unknown>
  new_value?: Record<string, unknown>
  effective_date?: string
  source?: string
  detected_at: string
}

import type { SchemeResult, SchemeDocumentItem } from '../types'

export const apiClient = {
  // Health
  health: () => api.get('/health/'),

  // Demo auto-login
  demoLogin: () => api.get('/auth/demo/'),

  // Google OAuth Login
  googleLogin: (data: { email: string; name?: string; picture?: string; google_id?: string }) =>
    api.post('/auth/google/', data),
  getGoogleConfig: () => api.get<{ client_id: string }>('/auth/google/config/'),

  // Profiles
  getProfiles: () => api.get<{ results: BusinessProfile[] }>('/profiles/'),
  getProfile: (id: string) => api.get<BusinessProfile>(`/profiles/${id}/`),
  createProfile: (data: Partial<BusinessProfile>) => api.post<BusinessProfile>('/profiles/', data),
  updateProfile: (id: string, data: Partial<BusinessProfile>) => api.patch<BusinessProfile>(`/profiles/${id}/`, data),

  // Goals
  submitGoal: (profileId: string, goalText: string, correlationId?: string) =>
    api.post<{
      goal: BusinessGoal
      strategy_id: string
      correlation_id?: string
      trace_id?: string
      status?: string
      steps?: Array<{
        step_name: string
        component: string
        status: string
        duration_ms: number
        output_summary: string
        trace_id: string
      }>
      evaluations_summary?: Record<string, number>
    }>(
      '/goals/submit/',
      {
        business_profile_id: profileId,
        goal_text: goalText,
      },
      correlationId
        ? {
            headers: {
              'X-Correlation-ID': correlationId,
              'X-Trace-ID': correlationId,
            },
          }
        : undefined
    ),
  getGoal: (id: string) => api.get<BusinessGoal>(`/goals/${id}/`),
  getGoals: () => api.get<{ results: BusinessGoal[] }>('/goals/'),

  // Strategy
  getStrategy: (id: string, correlationId?: string) =>
    api.get<Strategy>(
      `/strategies/${id}/`,
      correlationId
        ? {
            headers: {
              'X-Correlation-ID': correlationId,
              'X-Trace-ID': correlationId,
            },
          }
        : undefined
    ),
  getStrategyForGoal: (goalId: string) => api.get<Strategy>(`/strategies/for_goal/?goal_id=${goalId}`),

  // Schemes
  getSchemes: (params?: { search?: string; q?: string; level?: string; support_type?: string; category?: string; state?: string; division?: string; ministry?: string }) =>
    api.get<{ count: number; results: SchemeResult[] }>('/schemes/', { params }),
  getScheme: (id: string) => api.get<SchemeResult>(`/schemes/${id}/`),
  ragRecommend: (data: { query: string; sector?: string; msme_type?: string }) =>
    api.post<{
      query: string
      total_matches: number
      top_deal: SchemeResult & { match_score: number; recommendation_rationale: string[] }
      recommendations: Array<SchemeResult & { match_score: number; recommendation_rationale: string[] }>
    }>('/schemes/rag-recommend/', data),

  // Policy changes
  getPolicyChanges: () => api.get<{ count: number; results: PolicyChange[] }>('/policy-changes/'),
  simulatePolicyImpact: (schemeCode: string, simulatedChange: Record<string, unknown>, correlationId?: string) =>
    api.post(
      '/policy-monitoring/impact/demo-simulate/',
      {
        scheme_code: schemeCode,
        simulated_change: simulatedChange,
      },
      correlationId
        ? {
            headers: {
              'X-Correlation-ID': correlationId,
              'X-Trace-ID': correlationId,
            },
          }
        : undefined
    ),

  // Application Preparation Workspace
  getOrCreateWorkspace: (businessProfileId: string, schemeId: string, strategyId?: string) =>
    api.post('/workspaces/get-or-create/', {
      business_profile_id: businessProfileId,
      scheme_id: schemeId,
      strategy_id: strategyId,
    }),
  refreshWorkspace: (workspaceId: string) =>
    api.post(`/workspaces/${workspaceId}/refresh/`),
  markWorkspaceApplied: (workspaceId: string) =>
    api.post(`/workspaces/${workspaceId}/mark-applied/`),
}


export * from '../types'
export default api
