import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { renderWithProviders } from '../test-utils'
import PolicyMonitor from '../../pages/PolicyMonitor'
import { apiClient } from '../../api/client'
import { mockPolicyChanges } from '../fixtures/mockPolicyImpact'

vi.mock('../../api/client', () => ({
  apiClient: {
    getPolicyChanges: vi.fn(),
  },
}))

describe('PolicyMonitor Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(apiClient.getPolicyChanges).mockResolvedValue({
      data: { count: 2, results: mockPolicyChanges },
    } as any)
  })

  it('renders page header and policy change notifications banner', async () => {
    renderWithProviders(<PolicyMonitor />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 3, name: /Policy Monitor/i })).toBeInTheDocument()
      expect(screen.getByText(/2 Policy Changes Detected/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Re-evaluate Profile/i })).toBeInTheDocument()
    })
  })

  it('renders detected policy changes with change type labels and summaries', async () => {
    renderWithProviders(<PolicyMonitor />)

    await waitFor(() => {
      // First change: Benefit Increased
      expect(screen.getByText(/Gujarat Industrial Policy - Assistance to MSMEs/i)).toBeInTheDocument()
      expect(screen.getByText(/Benefit Increased/i)).toBeInTheDocument()
      expect(screen.getByText(/Capital subsidy for Category-1 talukas increased from 25% to 35%/i)).toBeInTheDocument()

      // Second change: Deadline Extended
      expect(screen.getByText(/Credit Linked Capital Subsidy Scheme \(CLCSS\)/i)).toBeInTheDocument()
      expect(screen.getByText(/Deadline Extended/i)).toBeInTheDocument()
    })
  })

  it('handles API error state gracefully', async () => {
    vi.mocked(apiClient.getPolicyChanges).mockRejectedValue(new Error('Network error'))
    renderWithProviders(<PolicyMonitor />)

    await waitFor(() => {
      expect(screen.getByText(/Failed to load policy changes/i)).toBeInTheDocument()
    })
  })
})
