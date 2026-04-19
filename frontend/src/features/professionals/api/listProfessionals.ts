import { apiRequest } from '@/shared/lib/apiClient'
import type { Paginated, Professional, ProfessionalSource } from '../types'

export type ListProfessionalsParams = {
  page?: number
  pageSize?: number
  source?: ProfessionalSource
}

export function listProfessionals(
  params: ListProfessionalsParams = {},
  signal?: AbortSignal,
): Promise<Paginated<Professional>> {
  const search = new URLSearchParams()
  if (params.page) search.set('page', String(params.page))
  if (params.pageSize) search.set('page_size', String(params.pageSize))
  if (params.source) search.set('source', params.source)

  const query = search.toString()
  const path = `/api/professionals/${query ? `?${query}` : ''}`

  return apiRequest<Paginated<Professional>>(
    path,
    signal ? { signal } : {},
  )
}
