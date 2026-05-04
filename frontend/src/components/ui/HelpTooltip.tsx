import { useState } from 'react'
import { InformationCircleIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface HelpTooltipProps {
  title: string
  description: string
  examples?: string[]
}

export function HelpTooltip({ title, description, examples }: HelpTooltipProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="ml-2 inline-flex items-center text-gray-400 hover:text-gray-600 transition-colors"
        title="Ayuda"
      >
        <InformationCircleIcon className="h-4 w-4" />
      </button>

      {isOpen && (
        <div className="absolute z-50 mt-2 w-80 p-4 bg-white border border-gray-200 rounded-lg shadow-lg">
          <div className="flex items-start justify-between">
            <h4 className="text-sm font-semibold text-gray-900">{title}</h4>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          </div>
          <p className="mt-2 text-sm text-gray-600">{description}</p>
          {examples && examples.length > 0 && (
            <div className="mt-3">
              <p className="text-xs font-medium text-gray-700 uppercase tracking-wide">Ejemplos:</p>
              <ul className="mt-1 text-sm text-gray-600 list-disc list-inside space-y-1">
                {examples.map((example, index) => (
                  <li key={index}>{example}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Componente para encabezados de gráficas con ayuda integrada
interface ChartHeaderProps {
  title: string
  help: {
    title: string
    description: string
    examples?: string[]
  }
}

export function ChartHeader({ title, help }: ChartHeaderProps) {
  return (
    <div className="flex items-center mb-4">
      <h2 className="text-sm font-semibold text-gray-700">{title}</h2>
      <HelpTooltip {...help} />
    </div>
  )
}
