import type { Professional } from '../types'

type ProfessionalsTableProps = {
  professionals: Professional[]
}

const SOURCE_STYLES: Record<Professional['source'], string> = {
  direct: 'bg-emerald-100 text-emerald-700',
  partner: 'bg-sky-100 text-sky-700',
  internal: 'bg-violet-100 text-violet-700',
}

export function ProfessionalsTable({ professionals }: ProfessionalsTableProps) {
  if (professionals.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center text-sm text-slate-500">
        No professionals yet. Click “+ Add” to create one.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-200">
        <thead>
          <tr className="text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
            <th className="px-4 py-3">Name</th>
            <th className="px-4 py-3">Email</th>
            <th className="px-4 py-3">Company</th>
            <th className="px-4 py-3">Title</th>
            <th className="px-4 py-3">Phone</th>
            <th className="px-4 py-3">Source</th>
            <th className="px-4 py-3">Created</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 text-sm text-slate-700">
          {professionals.map((professional) => (
            <tr key={professional.id} className="hover:bg-slate-50">
              <td className="whitespace-nowrap px-4 py-3 font-medium text-slate-900">
                {professional.full_name}
              </td>
              <td className="px-4 py-3 text-slate-600">
                {professional.email ?? '—'}
              </td>
              <td className="px-4 py-3">{professional.company_name}</td>
              <td className="px-4 py-3">{professional.job_title}</td>
              <td className="px-4 py-3 text-slate-600">
                {professional.phone ?? '—'}
              </td>
              <td className="px-4 py-3">
                <span
                  className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium capitalize ${SOURCE_STYLES[professional.source]}`}
                >
                  {professional.source}
                </span>
              </td>
              <td className="whitespace-nowrap px-4 py-3 text-slate-500">
                {new Date(professional.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
