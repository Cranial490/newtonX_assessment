import { useMemo, useRef, useState, type ChangeEvent, type KeyboardEvent } from 'react'
import { Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { apiRequest, ApiError } from '@/shared/lib/apiClient'
import { PROFESSIONAL_SOURCES, type ProfessionalSource } from '../types'

type Row = {
  id: string
  full_name: string
  email: string
  company_name: string
  job_title: string
  phone: string
  source: ProfessionalSource
  touched: { full_name?: boolean; email?: boolean; phone?: boolean }
}

type RowErrors = {
  full_name?: string
  email?: string
  phone?: string
}

type BulkResponse = {
  summary: { created: number; updated: number; failed: number; total: number }
  results: Array<{ index: number; status: string; errors?: unknown }>
}

const EMAIL_RE =
  /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$/
const PHONE_ALLOWED_RE = /^\+?[0-9\s().-]+$/

let rowCounter = 0
const newId = () => `r${++rowCounter}-${Date.now()}`

const blankRow = (): Row => ({
  id: newId(),
  full_name: '',
  email: '',
  company_name: '',
  job_title: '',
  phone: '',
  source: 'direct',
  touched: {},
})

const isEmptyRow = (row: Row) =>
  !row.full_name.trim() &&
  !row.email.trim() &&
  !row.company_name.trim() &&
  !row.job_title.trim() &&
  !row.phone.trim()

function validateRow(row: Row): RowErrors {
  const errors: RowErrors = {}
  if (!row.full_name.trim()) {
    errors.full_name = 'Full name is required.'
  }
  const email = row.email.trim()
  const phone = row.phone.trim()
  if (email && !EMAIL_RE.test(email)) {
    errors.email = 'Enter a valid email.'
  }
  if (phone) {
    const digits = phone.replace(/\D/g, '')
    if (!PHONE_ALLOWED_RE.test(phone) || digits.length < 7 || digits.length > 15) {
      errors.phone = 'Enter a valid phone number.'
    }
  }
  if (!email && !phone) {
    errors.email = 'Email or phone is required.'
  }
  return errors
}

function visibleErrors(row: Row): RowErrors {
  const raw = validateRow(row)
  const shown: RowErrors = {}
  const anyTouched = !!(row.touched.full_name || row.touched.email || row.touched.phone)
  if (row.touched.full_name && raw.full_name) shown.full_name = raw.full_name
  if (row.touched.email && raw.email) shown.email = raw.email
  if (row.touched.phone && raw.phone) shown.phone = raw.phone
  if (anyTouched && !row.email.trim() && !row.phone.trim()) {
    shown.email = 'Email or phone is required.'
    shown.phone = 'Email or phone is required.'
  }
  return shown
}

function submitBulk(records: unknown[]): Promise<BulkResponse> {
  return apiRequest<BulkResponse>('/api/professionals/bulk/', {
    method: 'POST',
    body: { records },
  })
}

export function BulkUploadPage() {
  const [rows, setRows] = useState<Row[]>(() => [blankRow()])
  const [submitMessage, setSubmitMessage] = useState<{ kind: 'success' | 'error'; text: string } | null>(null)
  const cellRefs = useRef(new Map<string, HTMLInputElement | HTMLSelectElement | null>())

  const registerCell = (rowId: string, field: string) => (el: HTMLInputElement | HTMLSelectElement | null) => {
    cellRefs.current.set(`${rowId}:${field}`, el)
  }

  const focusCell = (rowId: string, field: string) => {
    const el = cellRefs.current.get(`${rowId}:${field}`)
    if (el) {
      el.focus()
      if (el instanceof HTMLInputElement) el.select()
    }
  }

  const updateRow = (id: string, patch: Partial<Row>) => {
    setRows((prev) => prev.map((r) => (r.id === id ? { ...r, ...patch } : r)))
  }

  const markTouched = (id: string, field: keyof Row['touched']) => {
    setRows((prev) =>
      prev.map((r) => (r.id === id ? { ...r, touched: { ...r.touched, [field]: true } } : r)),
    )
  }

  const addRow = () => {
    const row = blankRow()
    setRows((prev) => [...prev, row])
    setTimeout(() => focusCell(row.id, 'full_name'), 0)
  }

  const removeRow = (id: string) => {
    setRows((prev) => (prev.length === 1 ? [blankRow()] : prev.filter((r) => r.id !== id)))
  }

  const handleEnter = (rowId: string) => (event: KeyboardEvent<HTMLElement>) => {
    if (event.key !== 'Enter') return
    event.preventDefault()
    const idx = rows.findIndex((r) => r.id === rowId)
    if (idx === rows.length - 1) {
      const row = blankRow()
      setRows((prev) => [...prev, row])
      setTimeout(() => focusCell(row.id, 'full_name'), 0)
    } else {
      focusCell(rows[idx + 1].id, 'full_name')
    }
  }

  const nonEmptyRows = useMemo(() => rows.filter((r) => !isEmptyRow(r)), [rows])
  const validRows = useMemo(
    () => nonEmptyRows.filter((r) => Object.keys(validateRow(r)).length === 0),
    [nonEmptyRows],
  )
  const errorRowCount = useMemo(
    () =>
      nonEmptyRows.filter(
        (r) =>
          (r.touched.full_name || r.touched.email || r.touched.phone) &&
          Object.keys(validateRow(r)).length > 0,
      ).length,
    [nonEmptyRows],
  )

  const bulkMutation = useMutation({
    mutationFn: submitBulk,
    onSuccess: (data) => {
      const { summary } = data
      setSubmitMessage({
        kind: 'success',
        text: `Submitted ${summary.total} record${summary.total === 1 ? '' : 's'} — ${summary.created} created, ${summary.updated} updated${summary.failed ? `, ${summary.failed} failed` : ''}.`,
      })
      if (summary.failed === 0) {
        setRows([blankRow()])
      }
    },
    onError: (error) => {
      const text =
        error instanceof ApiError
          ? `Submit failed (${error.status}).`
          : error instanceof Error
            ? error.message
            : 'Submit failed.'
      setSubmitMessage({ kind: 'error', text })
    },
  })

  const handleSubmit = () => {
    setSubmitMessage(null)
    const payload = validRows.map((r) => ({
      full_name: r.full_name.trim(),
      source: r.source,
      ...(r.email.trim() ? { email: r.email.trim().toLowerCase() } : {}),
      ...(r.company_name.trim() ? { company_name: r.company_name.trim() } : {}),
      ...(r.job_title.trim() ? { job_title: r.job_title.trim() } : {}),
      ...(r.phone.trim() ? { phone: r.phone.trim() } : {}),
    }))
    if (payload.length === 0) return
    bulkMutation.mutate(payload)
  }

  const submitLabel =
    validRows.length > 0
      ? `Submit ${validRows.length} record${validRows.length === 1 ? '' : 's'}`
      : 'Submit records'

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col gap-6 px-6 py-8">
      <header className="flex items-baseline justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Data Intake</h1>
          <p className="mt-1 text-sm text-slate-500">
            Add records manually or upload a CSV. Changes are validated in real time.
          </p>
        </div>
        <Link to="/" className="text-sm font-medium text-blue-600 hover:underline">
          ← Back to dashboard
        </Link>
      </header>

      <div className="flex flex-wrap items-center justify-end gap-2">
        <SecondaryButton icon="upload">Upload CSV</SecondaryButton>
        <SecondaryButton icon="plus" onClick={addRow}>
          Add row
        </SecondaryButton>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={validRows.length === 0 || bulkMutation.isPending}
          className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none"
        >
          <CheckIcon />
          {bulkMutation.isPending ? 'Submitting…' : submitLabel}
        </button>
      </div>

      {submitMessage ? (
        <div
          className={
            'rounded-xl border px-4 py-2.5 text-sm ' +
            (submitMessage.kind === 'success'
              ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
              : 'border-rose-200 bg-rose-50 text-rose-700')
          }
        >
          {submitMessage.text}
        </div>
      ) : null}

      <section
        aria-label="Data intake grid"
        className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
      >
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                <Th className="w-10 text-center"> </Th>
                <Th required>Full name</Th>
                <Th>Email</Th>
                <Th>Company</Th>
                <Th>Job title</Th>
                <Th>Phone</Th>
                <Th>Source</Th>
                <Th>Status</Th>
                <Th className="w-10 text-center"> </Th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {rows.map((row, index) => (
                <DataRow
                  key={row.id}
                  row={row}
                  index={index}
                  onChange={(patch) => updateRow(row.id, patch)}
                  onBlurField={(field) => markTouched(row.id, field)}
                  onEnter={handleEnter(row.id)}
                  onRemove={() => removeRow(row.id)}
                  registerCell={registerCell}
                />
              ))}
            </tbody>
          </table>
        </div>
        <div className="flex items-center justify-between border-t border-slate-200 bg-slate-50 px-4 py-2 text-xs text-slate-500">
          <div className="flex items-center gap-3">
            <span>
              {nonEmptyRows.length} record{nonEmptyRows.length === 1 ? '' : 's'}
            </span>
            {validRows.length > 0 ? (
              <span className="text-emerald-600">{validRows.length} ready</span>
            ) : null}
            {errorRowCount > 0 ? (
              <span className="text-rose-600">{errorRowCount} with errors</span>
            ) : null}
          </div>
          <span>* required</span>
        </div>
      </section>

    </main>
  )
}

type DataRowProps = {
  row: Row
  index: number
  onChange: (patch: Partial<Row>) => void
  onBlurField: (field: keyof Row['touched']) => void
  onEnter: (event: KeyboardEvent<HTMLElement>) => void
  onRemove: () => void
  registerCell: (rowId: string, field: string) => (el: HTMLInputElement | HTMLSelectElement | null) => void
}

function DataRow({ row, index, onChange, onBlurField, onEnter, onRemove, registerCell }: DataRowProps) {
  const errors = visibleErrors(row)
  const empty = isEmptyRow(row)
  const rawErrors = validateRow(row)
  const hasErrors = Object.keys(errors).length > 0
  const isValid = !empty && Object.keys(rawErrors).length === 0

  let rowClass = 'border-l-2 border-l-transparent hover:bg-slate-50'
  if (hasErrors) {
    rowClass = 'border-l-2 border-l-rose-500 bg-rose-50/60'
  } else if (isValid) {
    rowClass = 'border-l-2 border-l-emerald-500 hover:bg-slate-50'
  }

  let badge: React.ReactNode = <span className="text-slate-400">—</span>
  if (hasErrors) {
    badge = <Pill tone="danger">Error</Pill>
  } else if (isValid) {
    badge = <Pill tone="success">Ready</Pill>
  }

  return (
    <tr className={`group ${rowClass}`}>
      <td className="px-2 text-center text-xs text-slate-400">{index + 1}</td>
      <Cell error={errors.full_name}>
        <input
          ref={registerCell(row.id, 'full_name')}
          value={row.full_name}
          placeholder="Full name"
          onChange={(e: ChangeEvent<HTMLInputElement>) => onChange({ full_name: e.target.value })}
          onBlur={() => onBlurField('full_name')}
          onKeyDown={onEnter}
          className={cellInputClass(!!errors.full_name)}
        />
      </Cell>
      <Cell error={errors.email}>
        <input
          ref={registerCell(row.id, 'email')}
          value={row.email}
          placeholder="email@company.com"
          onChange={(e: ChangeEvent<HTMLInputElement>) => onChange({ email: e.target.value })}
          onBlur={() => onBlurField('email')}
          onKeyDown={onEnter}
          className={cellInputClass(!!errors.email)}
        />
      </Cell>
      <Cell>
        <input
          ref={registerCell(row.id, 'company_name')}
          value={row.company_name}
          placeholder="Company"
          onChange={(e: ChangeEvent<HTMLInputElement>) => onChange({ company_name: e.target.value })}
          onKeyDown={onEnter}
          className={cellInputClass(false)}
        />
      </Cell>
      <Cell>
        <input
          ref={registerCell(row.id, 'job_title')}
          value={row.job_title}
          placeholder="Job title"
          onChange={(e: ChangeEvent<HTMLInputElement>) => onChange({ job_title: e.target.value })}
          onKeyDown={onEnter}
          className={cellInputClass(false)}
        />
      </Cell>
      <Cell error={errors.phone}>
        <input
          ref={registerCell(row.id, 'phone')}
          value={row.phone}
          placeholder="+1 (555) 000-0000"
          onChange={(e: ChangeEvent<HTMLInputElement>) => onChange({ phone: e.target.value })}
          onBlur={() => onBlurField('phone')}
          onKeyDown={onEnter}
          className={cellInputClass(!!errors.phone)}
        />
      </Cell>
      <Cell>
        <select
          ref={registerCell(row.id, 'source')}
          value={row.source}
          onChange={(e: ChangeEvent<HTMLSelectElement>) =>
            onChange({ source: e.target.value as ProfessionalSource })
          }
          onKeyDown={onEnter}
          className={`${cellInputClass(false)} capitalize`}
        >
          {PROFESSIONAL_SOURCES.map((source) => (
            <option key={source} value={source}>
              {source}
            </option>
          ))}
        </select>
      </Cell>
      <td className="px-3 py-2">{badge}</td>
      <td className="w-10 px-2 text-center">
        <button
          type="button"
          onClick={onRemove}
          aria-label="Delete row"
          className="invisible rounded-full px-2 py-0.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 group-hover:visible"
        >
          ×
        </button>
      </td>
    </tr>
  )
}

function cellInputClass(hasError: boolean) {
  return (
    'block w-full bg-transparent px-2 py-2 text-sm outline-none placeholder:text-slate-400 focus:bg-slate-50 ' +
    (hasError ? 'text-rose-700' : 'text-slate-900')
  )
}

function Cell({ children, error }: { children: React.ReactNode; error?: string }) {
  return (
    <td className="h-10 border-l border-slate-100 px-0 align-middle first-of-type:border-l-0">
      <div className="flex flex-col">
        {children}
        {error ? <span className="px-2 pb-1 text-[11px] text-rose-600">{error}</span> : null}
      </div>
    </td>
  )
}

function Th({
  children,
  required,
  className = '',
}: {
  children: React.ReactNode
  required?: boolean
  className?: string
}) {
  return (
    <th className={`px-3 py-3 text-left font-semibold ${className}`}>
      {children}
      {required ? <span className="ml-0.5 text-rose-500">*</span> : null}
    </th>
  )
}

function Pill({ tone, children }: { tone: 'success' | 'danger'; children: React.ReactNode }) {
  const cls =
    tone === 'success'
      ? 'bg-emerald-100 text-emerald-700'
      : 'bg-rose-100 text-rose-700'
  return (
    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}>
      {children}
    </span>
  )
}

function SecondaryButton({
  children,
  onClick,
  icon,
}: {
  children: React.ReactNode
  onClick?: () => void
  icon?: 'upload' | 'plus'
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-slate-300"
    >
      {icon === 'upload' ? <UploadIcon /> : null}
      {icon === 'plus' ? <PlusIcon /> : null}
      {children}
    </button>
  )
}

function UploadIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 3v12" />
      <path d="M7 8l5-5 5 5" />
      <path d="M5 21h14" />
    </svg>
  )
}

function PlusIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 5v14M5 12h14" />
    </svg>
  )
}

function CheckIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
      <path d="M5 12l5 5L20 7" />
    </svg>
  )
}
