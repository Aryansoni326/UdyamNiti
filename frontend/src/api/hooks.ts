import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from './client'
import type { BusinessProfile, BusinessGoal, Strategy, SchemeResult, PolicyChange } from '../types'

// ─── Query Keys ───────────────────────────────────────────────────────────────

export const queryKeys = {
  profile: (id: string) => ['profile', id] as const,
  profiles: ['profiles'] as const,
  goal: (id: string) => ['goal', id] as const,
  strategy: (id: string) => ['strategy', id] as const,
  schemes: (filters?: Record<string, unknown>) => ['schemes', filters] as const,
  policyChanges: ['policyChanges'] as const,
}

// ─── Profiles ─────────────────────────────────────────────────────────────────

export function useProfiles() {
  return useQuery({
    queryKey: queryKeys.profiles,
    queryFn: async () => {
      const res = await apiClient.getProfiles()
      return res.data.results as unknown as BusinessProfile[]
    },
  })
}

export function useProfile(id: string | undefined) {
  return useQuery({
    queryKey: queryKeys.profile(id || ''),
    queryFn: async () => {
      if (!id) throw new Error('Profile ID is required')
      const res = await apiClient.getProfile(id)
      return res.data as unknown as BusinessProfile
    },
    enabled: Boolean(id),
  })
}

export function useCreateProfile() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: Partial<BusinessProfile>) => {
      const res = await apiClient.createProfile(data as any)
      return res.data as unknown as BusinessProfile
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.profiles })
    },
  })
}

// ─── Goals & Strategy ─────────────────────────────────────────────────────────

export function useGoal(id: string | undefined) {
  return useQuery({
    queryKey: queryKeys.goal(id || ''),
    queryFn: async () => {
      if (!id) throw new Error('Goal ID is required')
      const res = await apiClient.getGoal(id)
      return res.data as unknown as BusinessGoal
    },
    enabled: Boolean(id),
  })
}

export function useSubmitGoal() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ profileId, goalText }: { profileId: string; goalText: string }) => {
      const res = await apiClient.submitGoal(profileId, goalText)
      return res.data
    },
    onSuccess: (data) => {
      if (data?.strategy_id) {
        qc.invalidateQueries({ queryKey: queryKeys.strategy(data.strategy_id) })
      }
    },
  })
}

export function useStrategy(strategyId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.strategy(strategyId || ''),
    queryFn: async () => {
      if (!strategyId) throw new Error('Strategy ID is required')
      const res = await apiClient.getStrategy(strategyId)
      return res.data as unknown as Strategy
    },
    enabled: Boolean(strategyId),
  })
}

// ─── Schemes & Policies ───────────────────────────────────────────────────────

export function useSchemes(params?: { level?: string; support_type?: string }) {
  return useQuery({
    queryKey: queryKeys.schemes(params),
    queryFn: async () => {
      const res = await apiClient.getSchemes(params)
      return res.data.results as unknown as SchemeResult[]
    },
  })
}

export function useScheme(id: string | undefined) {
  return useQuery({
    queryKey: ['scheme', id],
    queryFn: async () => {
      if (!id) throw new Error('Scheme ID is required')
      const res = await apiClient.getScheme(id)
      return res.data
    },
    enabled: Boolean(id),
  })
}

export function usePolicyChanges() {
  return useQuery({
    queryKey: queryKeys.policyChanges,
    queryFn: async () => {
      const res = await apiClient.getPolicyChanges()
      return res.data.results as unknown as PolicyChange[]
    },
  })
}
