type StatsPanelProps = {
  total: number | undefined
}

export function StatsPanel({ total }: StatsPanelProps) {
  return (
    <section
      aria-label="Stats"
      className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
            Overview
          </p>
          <p className="mt-1 text-sm text-slate-400">
            More stats coming soon.
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
            Total professionals
          </p>
          <p className="mt-1 text-3xl font-semibold text-slate-900">
            {total ?? '—'}
          </p>
        </div>
      </div>
    </section>
  )
}
