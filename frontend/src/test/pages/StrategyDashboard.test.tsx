import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { renderWithProviders } from '../test-utils'
import StrategyDashboard from '../../pages/StrategyDashboard'
import { apiClient } from '../../api/client'
import { mockGoldenStrategy } from '../fixtures/mockStrategy'

vi.mock('../../api/client', () => ({
  apiClient: {
    getStrategy: vi.fn(),
  },
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ strategyId: 'strat-golden-001' }),
  }
})

describe('StrategyDashboard Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(apiClient.getStrategy).mockResolvedValue({
      data: mockGoldenStrategy,
    } as any)
  })

  it('renders loading state initially while fetching strategy', () => {
    // Return pending promise
    vi.mocked(apiClient.getStrategy).mockReturnValue(new Promise(() => {}))
    renderWithProviders(<StrategyDashboard />)

    expect(screen.getByText(/Synthesizing Government-Support Strategy.../i)).toBeInTheDocument()
  })

  it('renders error state when strategy fetch fails', async () => {
    vi.mocked(apiClient.getStrategy).mockRejectedValue(new Error('Strategy not found'))
    renderWithProviders(<StrategyDashboard />)

    await waitFor(() => {
      expect(screen.getByText(/Could Not Retrieve Strategy/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Reload Strategy/i })).toBeInTheDocument()
    })
  })

  it('renders strategy executive view with business goal and primary opportunity', async () => {
    renderWithProviders(<StrategyDashboard />)

    await waitFor(() => {
      // Enterprise title
      expect(screen.getByText(/ABC Engineering Works LLP/i)).toBeInTheDocument()
      // Stated business goal quote
      expect(screen.getByText(new RegExp(mockGoldenStrategy.goal.raw_goal_text, 'i'))).toBeInTheDocument()
      // Evidence verification chip
      expect(screen.getByText(/Official Evidence Verified/i)).toBeInTheDocument()
      // Narrative text
      expect(screen.getByText(/ABC Engineering Works is strongly positioned/i)).toBeInTheDocument()
    })
  })

  it('renders unlock cards and opens the unlock modal when clicked', async () => {
    renderWithProviders(<StrategyDashboard />)

    await waitFor(() => {
      expect(screen.getByText(/Unlock \+₹2\.5 Lakhs: Women \/ SC-ST Ownership Stake/i)).toBeInTheDocument()
    })

    const unlockBtn = screen.getByRole('button', { name: /Resolve & Unlock/i })
    fireEvent.click(unlockBtn)

    // Modal opens
    expect(screen.getByText(/Resolve Fact: Women \/ SC-ST Stake Declaration/i)).toBeInTheDocument()

    // Confirm button re-evaluates
    const confirmBtn = screen.getByRole('button', { name: /Save & Re-evaluate/i })
    fireEvent.click(confirmBtn)

    await waitFor(() => {
      expect(screen.queryByText(/Resolve Fact: Women \/ SC-ST Stake Declaration/i)).not.toBeInTheDocument()
    })
  })

  it('navigates to Opportunity Landscape tab and opens WhyThis evidence drawer', async () => {
    renderWithProviders(<StrategyDashboard />)

    await waitFor(() => {
      expect(screen.getByText(/Opportunity Landscape/i)).toBeInTheDocument()
    })

    // Click Opportunity Landscape tab
    const oppTab = screen.getByText(/Opportunity Landscape/i)
    fireEvent.click(oppTab)

    // Verify schemes are displayed
    await waitFor(() => {
      expect(screen.getByText(/Credit Linked Capital Subsidy Scheme \(CLCSS\)/i)).toBeInTheDocument()
      expect(screen.getByText(/Gujarat Industrial Policy - Assistance to MSMEs/i)).toBeInTheDocument()
    })

    // Click "Why This Scheme?" for CLCSS
    const whyButtons = screen.getAllByRole('button', { name: /Why This Scheme\?/i })
    fireEvent.click(whyButtons[0])

    // Drawer should open with details
    await waitFor(() => {
      expect(screen.getByText(/Why "Credit Linked Capital Subsidy Scheme \(CLCSS\)"\?/i)).toBeInTheDocument()
      expect(screen.getByText(/Enterprise Size Eligibility/i)).toBeInTheDocument()
    })
  })

  it('switches to Cross-Scheme Intelligence tab and displays stacking relationship', async () => {
    renderWithProviders(<StrategyDashboard />)

    await waitFor(() => {
      expect(screen.getByText(/Cross-Scheme Intelligence/i)).toBeInTheDocument()
    })

    // Click Cross-Scheme tab
    const relTab = screen.getByText(/Cross-Scheme Intelligence/i)
    fireEvent.click(relTab)

    await waitFor(() => {
      expect(screen.getByText(/Central CLCSS 15% subsidy stacks with Gujarat State 25% capital subsidy/i)).toBeInTheDocument()
    })
  })

  it('switches to Action Plan tab and shows prioritized action checklist', async () => {
    renderWithProviders(<StrategyDashboard />)

    await waitFor(() => {
      expect(screen.getByText(/Prioritized Action Plan/i)).toBeInTheDocument()
    })

    const actionTab = screen.getByText(/Prioritized Action Plan/i)
    fireEvent.click(actionTab)

    await waitFor(() => {
      expect(screen.getByText(/Obtain Term Loan In-Principle Sanction for CNC Machine/i)).toBeInTheDocument()
      expect(screen.getByText(/Complete Free Online ZED Pledge/i)).toBeInTheDocument()
      expect(screen.getByText(/File Intent on Gujarat Investor Portal \(IFP\)/i)).toBeInTheDocument()
    })
  })
})
