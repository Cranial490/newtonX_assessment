import { Link } from 'react-router-dom'

export function BulkUploadPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-4xl flex-col gap-6 px-6 py-8">
      <header className="flex items-baseline justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Bulk upload</h1>
        <Link
          to="/"
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          ← Back to dashboard
        </Link>
      </header>
      <section className="rounded-2xl border border-slate-200 bg-white p-8 text-sm text-slate-500 shadow-sm">
        CSV upload and manual bulk entry coming soon.
      </section>
    </main>
  )
}
