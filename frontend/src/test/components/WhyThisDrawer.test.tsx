import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { screen, fireEvent } from '@testing-library/react'
import { renderWithProviders } from '../test-utils'
import { WhyThisDrawer } from '../../components/WhyThisDrawer'
import { mockClcssScheme, mockZedScheme } from '../fixtures/mockStrategy'

describe('WhyThisDrawer Component', () => {
  it('does not render content when closed or scheme is null', () => {
    const { container } = renderWithProviders(
      <WhyThisDrawer open={false} onClose={vi.fn()} scheme={null} />
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders rationale, deterministic conditions, and citations when open', () => {
    const handleClose = vi.fn()
    renderWithProviders(
      <WhyThisDrawer open={true} onClose={handleClose} scheme={mockClcssScheme} />
    )

    // Title & Ministry
    expect(screen.getByText(/Why "Credit Linked Capital Subsidy Scheme \(CLCSS\)"\?/i)).toBeInTheDocument()
    expect(screen.getByText(/Ministry of Micro, Small and Medium Enterprises/i)).toBeInTheDocument()

    // Decision rationale
    expect(screen.getByText(/ABC Engineering qualifies for 15% capital subsidy/i)).toBeInTheDocument()

    // Deterministic conditions evaluated
    expect(screen.getByText(/Enterprise Size Eligibility/i)).toBeInTheDocument()
    expect(screen.getByText(/Manufacturing Activity Verification/i)).toBeInTheDocument()
    expect(screen.getByText(/Clause 3.1\(a\) - Target Beneficiaries/i)).toBeInTheDocument()

    // Official portal handoff button
    const portalButton = screen.getByRole('link', { name: /Apply on Official Scheme Portal/i })
    expect(portalButton).toHaveAttribute('href', 'https://clcss.dcmsme.gov.in')
    expect(portalButton).toHaveAttribute('target', '_blank')

    // Trust disclaimer
    expect(screen.getByText(/Trust Notice:/i)).toBeInTheDocument()

    // Close button triggers onClose
    const closeBtn = screen.getByLabelText(/Close why this drawer/i)
    fireEvent.click(closeBtn)
    expect(handleClose).toHaveBeenCalledTimes(1)
  })

  it('renders unlock action banner and triggers onUnlockClick callback for potential match scheme', () => {
    const handleUnlock = vi.fn()
    renderWithProviders(
      <WhyThisDrawer
        open={true}
        onClose={vi.fn()}
        scheme={mockZedScheme}
        onUnlockClick={handleUnlock}
      />
    )

    expect(screen.getByText(/Unlock Opportunity/i)).toBeInTheDocument()
    expect(screen.getByText(/Complete the free 5-minute online ZED Pledge/i)).toBeInTheDocument()

    const resolveBtn = screen.getByRole('button', { name: /Resolve Missing Facts/i })
    fireEvent.click(resolveBtn)
    expect(handleUnlock).toHaveBeenCalledWith('MSME_ZED')
  })
})
