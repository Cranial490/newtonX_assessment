import { PROFESSIONAL_SOURCES } from '../types'
import type { ProfessionalStats } from '../api/getProfessionalStats'

type StatsPanelProps = {
  stats: ProfessionalStats | undefined
}

export function StatsPanel({ stats }: StatsPanelProps) {
  const completionRate =
    stats && stats.total > 0
      ? Math.round((stats.complete / stats.total) * 100)
      : stats
        ? 0
        : undefined

  return (
    <section
      aria-label="Stats"
      className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <div className="flex flex-col gap-5">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
            Overview
          </p>
          <div className="mt-3 grid gap-4 sm:grid-cols-3">
            <Stat label="Total professionals" value={stats?.total} />
            <Stat label="Complete records" value={stats?.complete} />
            <Stat
              label="Data completeness"
              value={completionRate}
              suffix="%"
            />
          </div>
        </div>

        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
            By source
          </p>
          <div className="mt-3 grid gap-3 sm:grid-cols-3">
            {PROFESSIONAL_SOURCES.map((source) => (
              <Stat
                key={source}
                label={source}
                value={stats?.source_counts[source]}
                compact
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

function Stat({
  label,
  value,
  suffix = '',
  compact,
}: {
  label: string
  value: number | undefined
  suffix?: string
  compact?: boolean
}) {
  return (
    <div className="border-l border-slate-200 pl-4">
      <p className="text-xs font-medium uppercase text-slate-500">{label}</p>
      <p
        className={
          compact
            ? 'mt-1 text-xl font-semibold text-slate-900'
            : 'mt-1 text-3xl font-semibold text-slate-900'
        }
      >
        {value === undefined ? '—' : `${value}${suffix}`}
      </p>
    </div>
  )
}
