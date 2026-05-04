interface EmptyStateProps {
  title?: string
  description?: string
  className?: string
}

export default function EmptyState({
  title = 'No data',
  description = 'There is nothing to display for the selected period.',
  className = '',
}: EmptyStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center py-16 text-center ${className}`}>
      <div className="text-5xl mb-4 select-none text-gray-300">◎</div>
      <p className="text-gray-700 font-medium">{title}</p>
      <p className="text-gray-400 text-sm mt-1 max-w-xs">{description}</p>
    </div>
  )
}
