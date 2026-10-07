import { BusinessGoal } from '../../types'

export const mockCncGoal: BusinessGoal = {
  id: 'goal-cnc-50l',
  business_profile: 'prof-abc-001',
  raw_goal_text: 'I want to purchase a ₹50 lakh CNC machine to expand production capacity for precision engineering components.',
  parsed_objective: 'Purchase ₹50 Lakh CNC machinery to expand precision engineering capacity',
  parsed_project_type: 'machinery_purchase',
  parsed_investment_amount_lakhs: 50.0,
  parsed_support_categories: ['capital_subsidy', 'credit_guarantee', 'technology_adoption'],
  parsed_missing_info: [],
  status: 'ready',
  created_at: '2026-09-29T10:00:00Z',
}

export const mockGoalWithMissingInfo: BusinessGoal = {
  id: 'goal-solar-35l',
  business_profile: 'prof-abc-001',
  raw_goal_text: 'Install a 100 kW rooftop solar PV installation to lower monthly manufacturing electricity bills.',
  parsed_objective: 'Install 100 kW rooftop solar plant',
  parsed_project_type: 'green_energy',
  parsed_investment_amount_lakhs: 35.0,
  parsed_support_categories: ['capital_subsidy', 'technology_adoption'],
  parsed_missing_info: ['energy_audit_report', 'discom_sanctioned_load'],
  status: 'ready',
  created_at: '2026-09-29T11:15:00Z',
}
