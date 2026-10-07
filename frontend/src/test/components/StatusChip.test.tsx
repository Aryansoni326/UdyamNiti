import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { screen, fireEvent } from '@testing-library/react'
import { renderWithProviders } from '../test-utils'
import { StatusChip } from '../../components/StatusChip'

describe('StatusChip Component', () => {
  it('renders MATCH status chip with correct label and aria-label', () => {
    renderWithProviders(<StatusChip status="MATCH" />)
    const chip = screen.getByLabelText(/Eligibility status:.*MATCH/i)
    expect(chip).toBeInTheDocument()
    expect(screen.getByText(/MATCH/i)).toBeInTheDocument()
  })

  it('renders POTENTIAL_MATCH status chip', () => {
    renderWithProviders(<StatusChip status="POTENTIAL_MATCH" />)
    const chip = screen.getByLabelText(/Eligibility status:.*POTENTIAL MATCH/i)
    expect(chip).toBeInTheDocument()
    expect(screen.getByText(/POTENTIAL MATCH/i)).toBeInTheDocument()
  })

  it('renders UNKNOWN status chip', () => {
    renderWithProviders(<StatusChip status="UNKNOWN" />)
    const chip = screen.getByLabelText(/Eligibility status:.*UNKNOWN/i)
    expect(chip).toBeInTheDocument()
    expect(screen.getByText(/UNKNOWN/i)).toBeInTheDocument()
  })

  it('renders DOES_NOT_MATCH status chip', () => {
    renderWithProviders(<StatusChip status="DOES_NOT_MATCH" />)
    const chip = screen.getByLabelText(/Eligibility status:.*DOES NOT MATCH/i)
    expect(chip).toBeInTheDocument()
    expect(screen.getByText(/DOES NOT MATCH/i)).toBeInTheDocument()
  })

  it('renders REQUIRES_OFFICIAL_VERIFICATION status chip', () => {
    renderWithProviders(<StatusChip status="REQUIRES_OFFICIAL_VERIFICATION" />)
    const chip = screen.getByLabelText(/Eligibility status:.*OFFICIAL VERIFICATION/i)
    expect(chip).toBeInTheDocument()
    expect(screen.getByText(/OFFICIAL VERIFICATION/i)).toBeInTheDocument()
  })


  it('fires onClick callback when clicked', () => {
    const handleClick = vi.fn()
    renderWithProviders(<StatusChip status="MATCH" onClick={handleClick} />)
    const chip = screen.getByLabelText(/Eligibility status: MATCH/i)
    fireEvent.click(chip)
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('handles lowercase or unknown status gracefully', () => {
    renderWithProviders(<StatusChip status="custom_pending" />)
    expect(screen.getByText(/custom pending/i)).toBeInTheDocument()
  })
})
