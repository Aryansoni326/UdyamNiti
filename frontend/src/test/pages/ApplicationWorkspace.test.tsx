import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { renderWithProviders } from '../test-utils'
import ApplicationWorkspace from '../../pages/ApplicationWorkspace'
import { apiClient } from '../../api/client'
import { mockApplicationWorkspaceData } from '../fixtures/mockWorkspace'

vi.mock('../../api/client', () => ({
  apiClient: {
    getOrCreateWorkspace: vi.fn(),
    refreshWorkspace: vi.fn(),
    markWorkspaceApplied: vi.fn(),
  },
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ profileId: 'prof-abc-001', schemeId: 'sch-guj-002' }),
  }
})

describe('ApplicationWorkspace Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(apiClient.getOrCreateWorkspace).mockResolvedValue({
      data: mockApplicationWorkspaceData,
    } as any)
    vi.mocked(apiClient.refreshWorkspace).mockResolvedValue({
      data: { ...mockApplicationWorkspaceData, readiness_score: 90 },
    } as any)
    vi.mocked(apiClient.markWorkspaceApplied).mockResolvedValue({
      data: { status: 'applied_external' },
    } as any)
  })

  it('renders loading spinner while workspace is loading', () => {
    vi.mocked(apiClient.getOrCreateWorkspace).mockReturnValue(new Promise(() => {}))
    renderWithProviders(<ApplicationWorkspace />)

    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('renders workspace details, readiness meter, and official portal route', async () => {
    renderWithProviders(<ApplicationWorkspace />)

    await waitFor(() => {
      // Scheme Title
      expect(screen.getByText(/Gujarat Industrial Policy - Assistance to MSMEs/i)).toBeInTheDocument()
      // Enterprise Name
      expect(screen.getByText(/ABC Engineering Works LLP/i)).toBeInTheDocument()
      // Official portal card
      expect(screen.getByText(/Gujarat Investor Facilitation Portal \(IFP\)/i)).toBeInTheDocument()
    })

    // Official portal link
    const portalLink = screen.getByRole('link', { name: /Continue to Official Portal/i })
    expect(portalLink).toHaveAttribute('href', 'https://ifp.gujarat.gov.in')
    expect(portalLink).toHaveAttribute('target', '_blank')
  })

  it('renders required document checklist with uploaded vs missing statuses', async () => {
    renderWithProviders(<ApplicationWorkspace />)

    await waitFor(() => {
      expect(screen.getByText(/Udyam Registration Certificate/i)).toBeInTheDocument()
      expect(screen.getByText(/GST 3B Returns/i)).toBeInTheDocument()
      expect(screen.getByText(/Pro-forma Invoice \/ Machinery Quotation/i)).toBeInTheDocument()
      expect(screen.getByText(/Bank Sanction Letter for Term Loan/i)).toBeInTheDocument()
    })
  })

  it('allows user to confirm application submission on external portal', async () => {
    renderWithProviders(<ApplicationWorkspace />)

    await waitFor(() => {
      expect(screen.getByText(/I have already submitted on portal/i)).toBeInTheDocument()
    })

    // Open confirmation modal
    const markBtn = screen.getByRole('button', { name: /I have already submitted on portal/i })
    fireEvent.click(markBtn)

    // Verify dialog appears
    expect(screen.getByText(/Confirm Portal Submission/i)).toBeInTheDocument()

    // Confirm submission
    const confirmBtn = screen.getByRole('button', { name: /Yes, Mark as Applied/i })
    fireEvent.click(confirmBtn)

    await waitFor(() => {
      expect(apiClient.markWorkspaceApplied).toHaveBeenCalledWith('ws-guj-001')
      expect(screen.getByText(/Marked as submitted on external portal/i)).toBeInTheDocument()
    })
  })

  it('refreshes readiness score when refresh button is clicked', async () => {
    renderWithProviders(<ApplicationWorkspace />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Refresh Readiness/i })).toBeInTheDocument()
    })

    const refreshBtn = screen.getByRole('button', { name: /Refresh Readiness/i })
    fireEvent.click(refreshBtn)

    await waitFor(() => {
      expect(apiClient.refreshWorkspace).toHaveBeenCalledWith('ws-guj-001')
    })
  })
})
