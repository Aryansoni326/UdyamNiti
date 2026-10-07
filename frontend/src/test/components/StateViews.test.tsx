import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { screen, fireEvent } from '@testing-library/react'
import { renderWithProviders } from '../test-utils'
import { LoadingState, SchemeCardSkeleton, ErrorState, EmptyState } from '../../components/StateViews'

describe('StateViews Components', () => {
  describe('LoadingState', () => {
    it('renders default loading message and spinner', () => {
      renderWithProviders(<LoadingState />)
      expect(screen.getByText(/Analyzing MSME Policy Landscape.../i)).toBeInTheDocument()
      expect(screen.getByText(/Evaluating deterministic eligibility conditions/i)).toBeInTheDocument()
    })

    it('renders custom steps with progress indicators', () => {
      const steps = ['Step 1: Parsing goal', 'Step 2: Checking rules', 'Step 3: Stacking']
      renderWithProviders(
        <LoadingState
          message="Computing Eligibility"
          progressSteps={steps}
          currentStepIndex={1}
        />
      )
      expect(screen.getByText('Computing Eligibility')).toBeInTheDocument()
      expect(screen.getByText('Step 1: Parsing goal')).toBeInTheDocument()
      expect(screen.getByText('Step 2: Checking rules')).toBeInTheDocument()
      expect(screen.getByText('Step 3: Stacking')).toBeInTheDocument()
    })
  })

  describe('SchemeCardSkeleton', () => {
    it('renders skeleton placeholders without crashing', () => {
      const { container } = renderWithProviders(<SchemeCardSkeleton />)
      const skeletons = container.querySelectorAll('.MuiSkeleton-root')
      expect(skeletons.length).toBeGreaterThan(0)
    })
  })

  describe('ErrorState', () => {
    it('renders error title, message, and executes retry action', () => {
      const handleRetry = vi.fn()
      renderWithProviders(
        <ErrorState
          title="Policy Service Unavailable"
          message="Could not reach government rules engine."
          onRetry={handleRetry}
          retryLabel="Try Again"
        />
      )

      expect(screen.getByText('Policy Service Unavailable')).toBeInTheDocument()
      expect(screen.getByText('Could not reach government rules engine.')).toBeInTheDocument()

      const retryBtn = screen.getByRole('button', { name: /Try Again/i })
      fireEvent.click(retryBtn)
      expect(handleRetry).toHaveBeenCalledTimes(1)
    })
  })

  describe('EmptyState', () => {
    it('renders empty description and executes action button callback', () => {
      const handleAction = vi.fn()
      renderWithProviders(
        <EmptyState
          title="No Matching Schemes Found"
          description="Try broadening your business profile parameters or adjusting investment timeline."
          actionLabel="Explore Gujarat Policies"
          onAction={handleAction}
        />
      )

      expect(screen.getByText('No Matching Schemes Found')).toBeInTheDocument()
      expect(screen.getByText(/Try broadening your business profile/i)).toBeInTheDocument()

      const actionBtn = screen.getByRole('button', { name: /Explore Gujarat Policies/i })
      fireEvent.click(actionBtn)
      expect(handleAction).toHaveBeenCalledTimes(1)
    })
  })
})
