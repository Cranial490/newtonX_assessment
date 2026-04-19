import { useState } from 'react'
import { Modal } from '@/shared/components/Modal'
import { ApiError } from '@/shared/lib/apiClient'
import { useCreateProfessional } from '../hooks/useCreateProfessional'
import { PROFESSIONAL_SOURCES, type ProfessionalSource } from '../types'

type AddProfessionalModalProps = {
  open: boolean
  onClose: () => void
  onBulkUpload?: () => void
}

type FormState = {
  full_name: string
  email: string
  phone: string
  source: ProfessionalSource
}

type FieldErrors = Partial<Record<keyof FormState, string[]>> & {
  non_field_errors?: string[]
}

const INITIAL_STATE: FormState = {
  full_name: '',
  email: '',
  phone: '',
  source: 'direct',
}

export function AddProfessionalModal({
  open,
  onClose,
  onBulkUpload,
}: AddProfessionalModalProps) {
  const [form, setForm] = useState<FormState>(INITIAL_STATE)
  const [errors, setErrors] = useState<FieldErrors>({})
  const createMutation = useCreateProfessional()

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const reset = () => {
    setForm(INITIAL_STATE)
    setErrors({})
    createMutation.reset()
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    setErrors({})

    const payload = {
      full_name: form.full_name.trim(),
      source: form.source,
      ...(form.email.trim() ? { email: form.email.trim() } : {}),
      ...(form.phone.trim() ? { phone: form.phone.trim() } : {}),
    }

    if (!payload.email && !payload.phone) {
      setErrors({ non_field_errors: ['Either email or phone is required.'] })
      return
    }

    createMutation.mutate(payload, {
      onSuccess: () => {
        reset()
        onClose()
      },
      onError: (error) => {
        if (error instanceof ApiError && error.status === 400) {
          setErrors((error.body as FieldErrors) ?? {})
        } else {
          setErrors({
            non_field_errors: [
              error instanceof Error ? error.message : 'Something went wrong.',
            ],
          })
        }
      },
    })
  }

  return (
    <Modal open={open} onClose={handleClose} title="Add professional">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Field
          label="Full name"
          required
          value={form.full_name}
          onChange={(value) => update('full_name', value)}
          errors={errors.full_name}
        />
        <Field
          label="Email"
          type="email"
          value={form.email}
          onChange={(value) => update('email', value)}
          errors={errors.email}
        />
        <Field
          label="Phone"
          value={form.phone}
          onChange={(value) => update('phone', value)}
          errors={errors.phone}
        />
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-slate-700">
            Source <span className="text-rose-500">*</span>
          </label>
          <select
            value={form.source}
            onChange={(event) =>
              update('source', event.target.value as ProfessionalSource)
            }
            className="rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
          >
            {PROFESSIONAL_SOURCES.map((source) => (
              <option key={source} value={source}>
                {source}
              </option>
            ))}
          </select>
          <FieldErrorList errors={errors.source} />
        </div>

        <FieldErrorList errors={errors.non_field_errors} />

        <div className="mt-2 flex items-center justify-between gap-2">
          {onBulkUpload ? (
            <button
              type="button"
              onClick={() => {
                reset()
                onBulkUpload()
              }}
              disabled={createMutation.isPending}
              className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              Bulk upload
            </button>
          ) : (
            <span />
          )}
          <div className="flex gap-2">
          <button
            type="button"
            onClick={handleClose}
            disabled={createMutation.isPending}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {createMutation.isPending ? 'Saving…' : 'Save'}
          </button>
          </div>
        </div>
      </form>
    </Modal>
  )
}

type FieldProps = {
  label: string
  value: string
  onChange: (value: string) => void
  required?: boolean
  type?: string
  errors?: string[] | undefined
}

function Field({
  label,
  value,
  onChange,
  required,
  type = 'text',
  errors,
}: FieldProps) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-slate-700">
        {label}
        {required ? <span className="text-rose-500"> *</span> : null}
      </label>
      <input
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
      />
      <FieldErrorList errors={errors} />
    </div>
  )
}

function FieldErrorList({ errors }: { errors?: string[] | undefined }) {
  if (!errors?.length) return null
  return (
    <ul className="text-xs text-rose-600">
      {errors.map((message, index) => (
        <li key={index}>{message}</li>
      ))}
    </ul>
  )
}
