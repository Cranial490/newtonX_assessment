import { useQuery } from '@tanstack/react-query'
import { getProfessionalStats } from '../api/getProfessionalStats'

export const professionalStatsQueryKey = ['professional-stats'] as const

export function useProfessionalStats() {
  return useQuery({
    queryKey: professionalStatsQueryKey,
    queryFn: ({ signal }) => getProfessionalStats(signal),
  })
}
