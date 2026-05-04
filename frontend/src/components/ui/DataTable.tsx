import { useState } from 'react'

export interface Column<T> {
  key: string
  header: string
  render?: (row: T, index: number) => React.ReactNode
  className?: string
}

interface DataTableProps<T extends object> {
  columns: Column<T>[]
  data: T[]
  onRowClick?: (row: T) => void
  pageSize?: number
  emptyText?: string
  className?: string
}

function DataTable<T extends object>({
  columns,
  data,
  onRowClick,
  pageSize,
  emptyText = 'No data to display.',
  className = '',
}: DataTableProps<T>) {
  const [page, setPage] = useState(0)
  const paginated = pageSize ? data.slice(page * pageSize, (page + 1) * pageSize) : data
  const totalPages = pageSize ? Math.ceil(data.length / pageSize) : 1

  if (data.length === 0) {
    return <p className="py-8 text-center text-sm text-gray-400">{emptyText}</p>
  }

  return (
    <div className={className}>
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500 ${col.className ?? ''}`}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {paginated.map((row, i) => (
              <tr
                key={i}
                onClick={() => onRowClick?.(row)}
                className={`transition-colors ${onRowClick ? 'cursor-pointer hover:bg-purple-50' : 'hover:bg-gray-50'}`}
              >
                {columns.map((col) => (
                  <td key={col.key} className={`px-4 py-3 text-gray-700 ${col.className ?? ''}`}>
                    {col.render
                      ? col.render(row, i)
                      : String((row as Record<string, unknown>)[col.key] ?? '—')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {pageSize && totalPages > 1 && (
        <div className="mt-3 flex items-center justify-between text-sm text-gray-500">
          <span>
            {page * pageSize + 1}–{Math.min((page + 1) * pageSize, data.length)} of {data.length}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-3 py-1 rounded border border-gray-200 hover:bg-gray-50 disabled:opacity-40"
            >
              ‹ Prev
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page === totalPages - 1}
              className="px-3 py-1 rounded border border-gray-200 hover:bg-gray-50 disabled:opacity-40"
            >
              Next ›
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default DataTable
