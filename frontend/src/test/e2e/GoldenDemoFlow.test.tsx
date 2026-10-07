import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { renderWithProviders } from '../test-utils'
import App from '../../App'
import { apiClient } from '../../api/client'
import { mockAbcEngineeringProfile } from '../fixtures/mockProfile'
import { mockCncGoal } from '../fixtures/mockGoal'
import { mockGoldenStrategy } from '../fixtures/mockStrategy'
import { mockApplicationWorkspaceData } from '../fixtures/mockWorkspace'

vi.mock('../../api/client', () => ({
  apiClient: {
    demoLogin: vi.fn(),
    getProfiles: vi.fn(),
    createProfile: vi.fn(),
    submitGoal: vi.fn(),
    getStrategy: vi.fn(),
    getOrCreateWorkspace: vi.fn(),
    refreshWorkspace: vi.fn(),
    markWorkspaceApplied: vi.fn(),
    getPolicyChanges: vi.fn(),
  },
}))

describe('End-to-End Golden Demo Happy Path: ABC Engineering Works', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(apiClient.demoLogin).mockResolvedValue({ data: { user: 'demo-user' } } as any)
    vi.mocked(apiClient.getProfiles).mockResolvedValue({ data: { results: [mockAbcEngineeringProfile] } } as any)
    vi.mocked(apiClient.createProfile).mockResolvedValue({ data: mockAbcEngineeringProfile } as any)
    vi.mocked(apiClient.submitGoal).mockResolvedValue({
      data: { goal: mockCncGoal, strategy_id: 'strat-golden-001' },
    } as any)
    vi.mocked(apiClient.getStrategy).mockResolvedValue({
      data: mockGoldenStrategy,
    } as any)
    vi.mocked(apiClient.getOrCreateWorkspace).mockResolvedValue({
      data: mockApplicationWorkspaceData,
    } as any)
    vi.mocked(apiClient.markWorkspaceApplied).mockResolvedValue({
      data: { status: 'applied_external' },
    } as any)
    vi.mocked(apiClient.getPolicyChanges).mockResolvedValue({
      data: { count: 0, results: [] },
    } as any)
  })

  it('completes the entire end-to-end journey from goal onboarding to official portal preparation', async () => {
    // ─── STEP 1: Launch on Goal Onboarding Page ────────────────────────────────
    renderWithProviders(<App />, { initialEntries: ['/onboard'] })

    // Verify Goal Onboarding page loaded
    expect(screen.getByText(/What does your business want to achieve\?/i)).toBeInTheDocument()

    // Select the "Buy new machinery" preset (₹50L CNC machine)
    const machineryPresetBtn = screen.getByRole('button', { name: /Buy new machinery/i })
    fireEvent.click(machineryPresetBtn)

    // Verify structured parsed goal preview
    expect(screen.getByText(/Target Investment/i)).toBeInTheDocument()
    expect(screen.getByText(/₹ 50 Lakh/i)).toBeInTheDocument()
    expect(screen.getByText(/Capital Subsidy/i)).toBeInTheDocument()

    // ─── STEP 2: Answer Targeted Enterprise Profile Questions ─────────────────
    const nextBtn = screen.getByRole('button', { name: /Next: Targeted Profile Questions/i })
    fireEvent.click(nextBtn)

    // Verify profile questions rendered
    await waitFor(() => {
      expect(screen.getByText(/Targeted Enterprise Profile/i)).toBeInTheDocument()
      expect(screen.getByText(/Enterprise Size Category/i)).toBeInTheDocument()
      expect(screen.getByText(/Operating District/i)).toBeInTheDocument()
    })

    // Click "Generate Policy Strategy" to execute orchestrator pipeline
    const generateBtn = screen.getByRole('button', { name: /Generate Policy Strategy/i })
    fireEvent.click(generateBtn)

    // Verify loading orchestration view displays
    await waitFor(() => {
      expect(screen.getByText(/Analyzing MSME Policies/i)).toBeInTheDocument()
    })

    // ─── STEP 3: Arrive on Strategy Dashboard ────────────────────────────────
    await waitFor(
      () => {
        expect(screen.getByText(/ABC Engineering Works LLP/i)).toBeInTheDocument()
        expect(screen.getByText(/Official Evidence Verified/i)).toBeInTheDocument()
      },
      { timeout: 5000 }
    )

    // Verify narrative and strategic recommendations
    expect(screen.getByText(/ABC Engineering Works is strongly positioned/i)).toBeInTheDocument()

    // Verify unlock cards are visible
    expect(screen.getByText(/Unlock \+₹2\.5 Lakhs: Women \/ SC-ST Ownership Stake/i)).toBeInTheDocument()

    // ─── STEP 4: Inspect Opportunity Landscape & Open "Why This?" Drawer ─────
    const oppLandscapeTab = screen.getByText(/Opportunity Landscape/i)
    fireEvent.click(oppLandscapeTab)

    await waitFor(() => {
      expect(screen.getByText(/Credit Linked Capital Subsidy Scheme \(CLCSS\)/i)).toBeInTheDocument()
      expect(screen.getByText(/Gujarat Industrial Policy - Assistance to MSMEs/i)).toBeInTheDocument()
    })

    // Click "Why This Scheme?" button on CLCSS
    const whyBtns = screen.getAllByRole('button', { name: /Why This Scheme\?/i })
    fireEvent.click(whyBtns[0])

    // Verify drawer displays official statutory evidence and legal disclaimers
    await waitFor(() => {
      expect(screen.getByText(/Why "Credit Linked Capital Subsidy Scheme \(CLCSS\)"\?/i)).toBeInTheDocument()
      expect(screen.getByText(/Enterprise Size Eligibility/i)).toBeInTheDocument()
      expect(screen.getByText(/Trust Notice:/i)).toBeInTheDocument()
    })

    // Close the drawer
    const closeDrawerBtn = screen.getByLabelText(/Close why this drawer/i)
    fireEvent.click(closeDrawerBtn)

    // ─── STEP 5: Verify Cross-Scheme Stacking Intelligence ────────────────────
    const crossSchemeTab = screen.getByText(/Cross-Scheme Intelligence/i)
    fireEvent.click(crossSchemeTab)

    await waitFor(() => {
      expect(screen.getByText(/Central CLCSS 15% subsidy stacks with Gujarat State 25% capital subsidy/i)).toBeInTheDocument()
    })
  })
})
