interface StatBadgeProps {
  label: string
  value: string | number
  unit?: string
  variant?: 'default' | 'success' | 'warning' | 'info'
}

export function StatBadge({ label, value, unit, variant = 'default' }: StatBadgeProps) {
  const getVariantClasses = () => {
    switch (variant) {
      case 'success':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'info':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getVariantClasses()}`}>
      <span className="font-semibold">{label}:</span>
      <span className="ml-1">{value}</span>
      {unit && <span className="ml-1 text-xs opacity-75">{unit}</span>}
    </div>
  )
}