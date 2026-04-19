import { ApiError } from '@/shared/lib/apiClient'
import { ProfessionalsTable } from '../components/ProfessionalsTable'
import { StatsPanel } from '../components/StatsPanel'
import { useProfessionals } from '../hooks/useProfessionals'

export function DashboardPage() {
  const { data, isPending, isError, error, refetch, isFetching } =
    useProfessionals()

  const handleAdd = () => {
    // Placeholder — wire up in the Add feature.
    console.log('Add clicked')
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col gap-6 px-6 py-8">
      <header className="flex items-baseline justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Professionals</h1>
        <p className="text-sm text-slate-500">
          {isFetching ? 'Refreshing…' : 'Dashboard'}
        </p>
      </header>

      <StatsPanel total={data?.count} />

      <div className="flex justify-end">
        <button
          type="button"
          onClick={handleAdd}
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-slate-400"
        >
          + Add
        </button>
      </div>

      <section
        aria-label="Professionals list"
        className="rounded-2xl border border-slate-200 bg-white shadow-sm"
      >
        {isPending ? (
          <div className="flex h-48 items-center justify-center text-sm text-slate-500">
            Loading professionals…
          </div>
        ) : isError ? (
          <ErrorState error={error} onRetry={() => refetch()} />
        ) : (
          <ProfessionalsTable professionals={data.results} />
        )}
      </section>
    </main>
  )
}

function ErrorState({ error, onRetry }: { error: unknown; onRetry: () => void }) {
  const message =
    error instanceof ApiError
      ? `Failed to load (${error.status})`
      : error instanceof Error
        ? error.message
        : 'Failed to load professionals.'

  return (
    <div className="flex h-48 flex-col items-center justify-center gap-3 text-sm text-slate-600">
      <p>{message}</p>
      <button
        type="button"
        onClick={onRetry}
        className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
      >
        Retry
      </button>
    </div>
  )
}
