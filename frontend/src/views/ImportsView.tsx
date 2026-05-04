import { useRef, useState } from 'react'
import axios from 'axios'
import { useImports } from '@/viewmodels/useImports'
import type { ImportResult } from '@/types/imports'
import Spinner from '@/components/ui/Spinner'

// ── Helpers ───────────────────────────────────────────────────────────────────

function extractError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = (err.response?.data as { detail?: string })?.detail
    return detail ?? `Upload failed (HTTP ${err.response?.status ?? '?'})`
  }
  return err instanceof Error ? err.message : 'Upload failed'
}

function resultMessage(r: ImportResult): string {
  if (r.period_start && r.period_end) {
    return `${r.rows_inserted} rows imported · ${r.period_start} → ${r.period_end}`
  }
  return `${r.rows_inserted} rows imported`
}

// ── UploadZone ────────────────────────────────────────────────────────────────

interface UploadZoneProps {
  label: string
  fileType: string          // human label: "PDF" | "Excel (.xlsx)"
  accept: string            // input accept attr: ".pdf" | ".xlsx"
  onUpload: (file: File) => Promise<ImportResult>
}

function UploadZone({ label, fileType, accept, onUpload }: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<ImportResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function processFile(file: File) {
    const expectedExt = accept
    if (!file.name.toLowerCase().endsWith(expectedExt)) {
      setError(`File must be a ${fileType} file (${expectedExt})`)
      setResult(null)
      return
    }
    setError(null)
    setResult(null)
    setIsLoading(true)
    try {
      const r = await onUpload(file)
      setResult(r)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setIsLoading(false)
    }
  }

  function onDragOver(e: React.DragEvent) {
    e.preventDefault()
    setIsDragging(true)
  }

  function onDragLeave(e: React.DragEvent) {
    e.preventDefault()
    setIsDragging(false)
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) void processFile(file)
  }

  function onInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) {
      void processFile(file)
      e.target.value = '' // allow re-uploading the same file
    }
  }

  const borderClass = isDragging
    ? 'border-purple-500 bg-purple-50'
    : error
      ? 'border-red-300 bg-red-50'
      : result
        ? 'border-emerald-300 bg-emerald-50'
        : 'border-gray-300 bg-white hover:border-purple-400 hover:bg-purple-50'

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label={`Upload ${label}`}
      onClick={() => !isLoading && inputRef.current?.click()}
      onKeyDown={(e) => e.key === 'Enter' && !isLoading && inputRef.current?.click()}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      className={`relative flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-8 cursor-pointer transition-colors select-none ${borderClass}`}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={onInputChange}
      />

      {isLoading ? (
        <>
          <Spinner size="lg" />
          <p className="text-sm font-medium text-gray-500">Uploading…</p>
        </>
      ) : result ? (
        <>
          <span className="text-4xl select-none">✓</span>
          <div className="text-center">
            <p className="text-sm font-semibold text-emerald-700">{label}</p>
            <p className="text-xs text-emerald-600 mt-0.5">{resultMessage(result)}</p>
          </div>
          <p className="text-xs text-gray-400">Click or drop to re-upload</p>
        </>
      ) : (
        <>
          <span className="text-4xl select-none text-gray-300">↑</span>
          <div className="text-center">
            <p className="text-sm font-semibold text-gray-700">{label}</p>
            <p className="text-xs text-gray-400 mt-0.5">{fileType}</p>
          </div>
          <p className="text-xs text-gray-400">Drag & drop or click to browse</p>
        </>
      )}

      {error && (
        <div className="absolute bottom-3 left-3 right-3 rounded-md bg-red-100 border border-red-200 px-3 py-2 text-xs text-red-700 text-center">
          {error}
        </div>
      )}
    </div>
  )
}

// ── ImportsView ───────────────────────────────────────────────────────────────

export default function ImportsView() {
  const {
    uploadDailySales,
    uploadHoursSummary,
    uploadHoursDetail,
    uploadWip,
    isUploading,
    lastResult,
  } = useImports()

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900">Import Data</h1>
        <p className="text-sm text-gray-500 mt-1">
          Upload the monthly reports from Automania. Each import replaces the
          existing data for that period.
        </p>
      </div>

      {lastResult && (
        <div className="rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-3 text-sm text-emerald-800">
          <span className="font-medium">Last import:</span> {lastResult.message}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <UploadZone
          label="Daily Sales"
          fileType="PDF"
          accept=".pdf"
          onUpload={uploadDailySales}
        />
        <UploadZone
          label="Hours Summary"
          fileType="PDF"
          accept=".pdf"
          onUpload={uploadHoursSummary}
        />
        <UploadZone
          label="Hours Detail"
          fileType="PDF"
          accept=".pdf"
          onUpload={uploadHoursDetail}
        />
        <UploadZone
          label="Work in Progress"
          fileType="Excel (.xlsx)"
          accept=".xlsx"
          onUpload={uploadWip}
        />
      </div>

      {isUploading && (
        <p className="text-center text-xs text-gray-400">Upload in progress…</p>
      )}
    </div>
  )
}
