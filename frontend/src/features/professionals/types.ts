export const PROFESSIONAL_SOURCES = ['direct', 'partner', 'internal'] as const
export type ProfessionalSource = (typeof PROFESSIONAL_SOURCES)[number]

export type Professional = {
  id: number
  full_name: string
  email: string | null
  company_name: string
  job_title: string
  phone: string | null
  source: ProfessionalSource
  created_at: string
}

export type Paginated<T> = {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
