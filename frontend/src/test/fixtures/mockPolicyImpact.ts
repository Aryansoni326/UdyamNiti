import { PolicyChange } from '../../types'

export const mockPolicyChanges: PolicyChange[] = [
  {
    id: 'pc-001',
    scheme_name: 'Gujarat Industrial Policy - Assistance to MSMEs',
    scheme_code: 'GUJ_MSME_SCHEME_2020',
    change_type: 'benefit_increased',
    change_summary: 'Capital subsidy for Category-1 talukas increased from 25% to 35% for automated precision machinery.',
    old_value: { subsidy_pct: 25.0, max_cap_lakhs: 25.0 },
    new_value: { subsidy_pct: 35.0, max_cap_lakhs: 35.0 },
    effective_date: '2026-09-15',
    source: 'Government Resolution No. GIP-2026-REV',
    detected_at: '2026-09-20T08:00:00Z',
  },
  {
    id: 'pc-002',
    scheme_name: 'Credit Linked Capital Subsidy Scheme (CLCSS)',
    scheme_code: 'MSME_CLCSS',
    change_type: 'deadline_extended',
    change_summary: 'Application window for FY26 term loan approvals extended by 6 months until March 2027.',
    old_value: { application_deadline: '2026-09-30' },
    new_value: { application_deadline: '2027-03-31' },
    effective_date: '2026-09-01',
    source: 'Ministry of MSME Circular 14/2026',
    detected_at: '2026-09-22T10:30:00Z',
  },
]
