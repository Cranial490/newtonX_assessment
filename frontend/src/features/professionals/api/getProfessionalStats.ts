import { apiRequest } from '@/shared/lib/apiClient'
import type { ProfessionalSource } from '../types'

export type ProfessionalStats = {
  total: number
  complete: number
  source_counts: Record<ProfessionalSource, number>
}

export function getProfessionalStats(
  signal?: AbortSignal,
): Promise<ProfessionalStats> {
  return apiRequest<ProfessionalStats>(
    '/api/professionals/stats/',
    signal ? { signal } : {},
  )
}
