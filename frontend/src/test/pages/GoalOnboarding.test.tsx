import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { renderWithProviders } from '../test-utils'
import GoalOnboarding from '../../pages/GoalOnboarding'
import { apiClient } from '../../api/client'
import { mockAbcEngineeringProfile } from '../fixtures/mockProfile'
import { mockCncGoal } from '../fixtures/mockGoal'

// Mock apiClient methods
vi.mock('../../api/client', () => ({
  apiClient: {
    demoLogin: vi.fn(),
    getProfiles: vi.fn(),
    createProfile: vi.fn(),
    submitGoal: vi.fn(),
  },
}))

// Mock useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ state: null }),
  }
})

describe('GoalOnboarding Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(apiClient.demoLogin).mockResolvedValue({ data: { user: 'demo' } } as any)
    vi.mocked(apiClient.getProfiles).mockResolvedValue({ data: { results: [mockAbcEngineeringProfile] } } as any)
    vi.mocked(apiClient.createProfile).mockResolvedValue({ data: mockAbcEngineeringProfile } as any)
    vi.mocked(apiClient.submitGoal).mockResolvedValue({
      data: { goal: mockCncGoal, strategy_id: 'strat-golden-001' },
    } as any)
  })

  it('renders initial step 0 with natural language goal input and preset goals', () => {
    renderWithProviders(<GoalOnboarding />)

    // Heading & Subheading
    expect(screen.getByText(/What does your business want to achieve\?/i)).toBeInTheDocument()

    // Preset buttons
    expect(screen.getByText(/Buy new machinery/i)).toBeInTheDocument()
    expect(screen.getByText(/Expand factory floor/i)).toBeInTheDocument()
    expect(screen.getByText(/Start exporting/i)).toBeInTheDocument()

    // 1-click benchmark button
    expect(screen.getByText(/1-Click Demo Benchmark/i)).toBeInTheDocument()
  })

  it('displays parsed goal review section with objective, project type, and categories', () => {
    renderWithProviders(<GoalOnboarding />)

    // Benchmark default pre-fills ₹50L CNC machine
    expect(screen.getByText(/Objective & Intent/i)).toBeInTheDocument()
    expect(screen.getByText(/Project Type/i)).toBeInTheDocument()
    expect(screen.getByText(/Target Investment/i)).toBeInTheDocument()
    expect(screen.getByText(/₹ 50 Lakh/i)).toBeInTheDocument()

    // Support categories chips
    expect(screen.getByText(/Capital Subsidy/i)).toBeInTheDocument()
    expect(screen.getByText(/Credit Guarantee/i)).toBeInTheDocument()
  })

  it('allows switching language to Gujarati and translates goal input presets', () => {
    renderWithProviders(<GoalOnboarding />)

    const langToggleBtn = screen.getByRole('button', { name: /English/i })
    fireEvent.click(langToggleBtn)

    // Preset buttons should switch to Gujarati
    expect(screen.getByText(/નવી મશીનરી ખરીદો/i)).toBeInTheDocument()
  })

  it('navigates to step 1 (profile questions) when Next button is clicked', () => {
    renderWithProviders(<GoalOnboarding />)

    const nextBtn = screen.getByRole('button', { name: /Next: Targeted Profile Questions/i })
    fireEvent.click(nextBtn)

    // Step 1 content
    expect(screen.getByText(/Targeted Enterprise Profile/i)).toBeInTheDocument()
    expect(screen.getByText(/Enterprise Size Category/i)).toBeInTheDocument()
    expect(screen.getByText(/Operating District/i)).toBeInTheDocument()
    expect(screen.getByText(/Ahmedabad/i)).toBeInTheDocument()
    expect(screen.getByText(/Manufacturing Unit/i)).toBeInTheDocument()
  })

  it('executes pipeline and submits goal to create strategy', async () => {
    renderWithProviders(<GoalOnboarding />)

    // Move to step 1
    const nextBtn = screen.getByRole('button', { name: /Next: Targeted Profile Questions/i })
    fireEvent.click(nextBtn)

    // Click Generate Policy Strategy
    const generateBtn = screen.getByRole('button', { name: /Generate Policy Strategy/i })
    fireEvent.click(generateBtn)

    // Step 2 loading progress
    await waitFor(() => {
      expect(screen.getByText(/Analyzing MSME Policies/i)).toBeInTheDocument()
    })

    // Submits and navigates to strategy dashboard
    await waitFor(
      () => {
        expect(apiClient.submitGoal).toHaveBeenCalled()
        expect(mockNavigate).toHaveBeenCalledWith('/strategy/strat-golden-001')
      },
      { timeout: 4000 }
    )
  })
})
