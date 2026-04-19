import { useQuery } from '@tanstack/react-query'
import { listProfessionals, type ListProfessionalsParams } from '../api/listProfessionals'

export function professionalsQueryKey(params: ListProfessionalsParams) {
  return ['professionals', params] as const
}

export function useProfessionals(params: ListProfessionalsParams = {}) {
  return useQuery({
    queryKey: professionalsQueryKey(params),
    queryFn: ({ signal }) => listProfessionals(params, signal),
  })
}
