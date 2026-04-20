import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  createProfessional,
  type CreateProfessionalInput,
} from '../api/createProfessional'
import { professionalStatsQueryKey } from './useProfessionalStats'

export function useCreateProfessional() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (input: CreateProfessionalInput) => createProfessional(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['professionals'] })
      queryClient.invalidateQueries({ queryKey: professionalStatsQueryKey })
    },
  })
}
