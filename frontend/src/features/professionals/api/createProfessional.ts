import { apiRequest } from '@/shared/lib/apiClient'
import type { Professional, ProfessionalSource } from '../types'

export type CreateProfessionalInput = {
  full_name: string
  source: ProfessionalSource
  email?: string
  phone?: string
  company_name?: string
  job_title?: string
}

export function createProfessional(
  input: CreateProfessionalInput,
): Promise<Professional> {
  return apiRequest<Professional>('/api/professionals/', {
    method: 'POST',
    body: input,
  })
}
