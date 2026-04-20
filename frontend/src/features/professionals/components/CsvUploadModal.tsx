import { useRef, useState, type ChangeEvent } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Modal } from '@/shared/components/Modal'
import { ApiError } from '@/shared/lib/apiClient'

export type CsvRecord = {
  full_name: string
  email?: string | null
  company_name?: string | null
  job_title?: string | null
  phone?: string | null
  source: string
}

export type CsvUploadRecord = {
  index: number
  status: 'valid' | 'failed'
  record: Partial<CsvRecord>
  errors?: Record<string, string[] | string>
}

export type CsvUploadResult = {
  summary: {
    total: number
    valid: number
    failed: number
  }
  records: CsvUploadRecord[]
}

type CsvUploadModalProps = {
  open: boolean
  onClose: () => void
  onImported: (result: CsvUploadResult) => void
}

function isCsvFile(file: File) {
  if (/\.csv$/i.test(file.name)) return true
  const type = file.type
  return (
    type === 'text/csv' ||
    type === 'application/csv' ||
    type === 'application/vnd.ms-excel'
  )
}

async function uploadCsv(file: File): Promise<CsvUploadResult> {
  const form = new FormData()
  form.append('file', file)

  const response = await fetch('/api/professionals/upload/csv/', {
    method: 'POST',
    body: form,
  })

  const contentType = response.headers.get('content-type') ?? ''
  const payload = contentType.includes('application/json')
    ? await response.json()
    : await response.text()

  if (!response.ok) {
    throw new ApiError(`Request failed: ${response.status}`, response.status, payload)
  }

  return payload as CsvUploadResult
}

export function CsvUploadModal({ open, onClose, onImported }: CsvUploadModalProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [fileError, setFileError] = useState<string | null>(null)
  const [apiError, setApiError] = useState<string | null>(null)
  const [result, setResult] = useState<CsvUploadResult | null>(null)

  const uploadMutation = useMutation({
    mutationFn: uploadCsv,
    onSuccess: (data) => {
      setResult(data)
      setApiError(null)
    },
    onError: (error) => {
      setResult(null)
      if (error instanceof ApiError) {
        const body = error.body as { file?: string[] } | string
        if (typeof body === 'object' && body?.file?.length) {
          setApiError(body.file[0] ?? 'Upload failed.')
        } else {
          setApiError(`Upload failed (${error.status}).`)
        }
      } else {
        setApiError(error instanceof Error ? error.message : 'Upload failed.')
      }
    },
  })

  const reset = () => {
    setFile(null)
    setFileError(null)
    setApiError(null)
    setResult(null)
    uploadMutation.reset()
    if (inputRef.current) inputRef.current.value = ''
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setApiError(null)
    setResult(null)
    const picked = event.target.files?.[0] ?? null
    if (!picked) {
      setFile(null)
      setFileError(null)
      return
    }
    if (!isCsvFile(picked)) {
      setFile(null)
      setFileError('Please select a .csv file.')
      return
    }
    setFile(picked)
    setFileError(null)
  }

  const handleUpload = () => {
    if (!file) return
    uploadMutation.mutate(file)
  }

  const handleUseRecords = () => {
    if (!result) return
    onImported(result)
    handleClose()
  }

  return (
    <Modal open={open} onClose={handleClose} title="Upload CSV">
      <div className="flex flex-col gap-4">
        <p className="text-sm text-slate-600">
          Upload a CSV with columns <code className="rounded bg-slate-100 px-1">full_name</code>,{' '}
          <code className="rounded bg-slate-100 px-1">email</code>,{' '}
          <code className="rounded bg-slate-100 px-1">phone</code>,{' '}
          <code className="rounded bg-slate-100 px-1">company_name</code>,{' '}
          <code className="rounded bg-slate-100 px-1">job_title</code>,{' '}
          <code className="rounded bg-slate-100 px-1">source</code>. Valid rows will be loaded into the grid for review before submit.
        </p>

        <div>
          <label className="flex cursor-pointer flex-col items-center justify-center gap-1 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-sm text-slate-600 transition hover:bg-slate-100">
            <span className="font-medium text-slate-700">
              {file ? file.name : 'Click to choose a CSV file'}
            </span>
            {file ? (
              <span className="text-xs text-slate-500">
                {(file.size / 1024).toFixed(1)} KB
              </span>
            ) : (
              <span className="text-xs text-slate-500">.csv, UTF-8 encoded</span>
            )}
            <input
              ref={inputRef}
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileChange}
              className="hidden"
            />
          </label>
          {fileError ? (
            <p className="mt-2 text-xs text-rose-600">{fileError}</p>
          ) : null}
        </div>

        {apiError ? (
          <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
            {apiError}
          </div>
        ) : null}

        {result ? (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
            <p className="font-medium">Parsed {result.summary.total} row{result.summary.total === 1 ? '' : 's'}.</p>
            <p className="text-xs text-emerald-700">
              {result.summary.valid} valid row{result.summary.valid === 1 ? '' : 's'} ready to load.
              {result.summary.failed > 0
                ? ` ${result.summary.failed} row${
                    result.summary.failed === 1 ? '' : 's'
                  } failed validation.`
                : ''}
            </p>
          </div>
        ) : null}

        <div className="flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={handleClose}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Cancel
          </button>
          {result ? (
            <button
              type="button"
              onClick={handleUseRecords}
              disabled={result.summary.valid === 0}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
            >
              Load rows
            </button>
          ) : (
            <button
              type="button"
              onClick={handleUpload}
              disabled={!file || uploadMutation.isPending}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
            >
              {uploadMutation.isPending ? 'Uploading…' : 'Upload'}
            </button>
          )}
        </div>
      </div>
    </Modal>
  )
}
