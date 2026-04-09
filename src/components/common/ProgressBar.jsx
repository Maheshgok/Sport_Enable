export default function ProgressBar({ value, max = 100, variant = 'default', showLabel = false, className = '' }) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))
  
  const variants = {
    default: 'bg-gray-900',
    success: 'bg-green-600',
    warning: 'bg-orange-500',
    info: 'bg-blue-600',
  }

  return (
    <div className={className}>
      {showLabel && (
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm text-gray-600">Progress</span>
          <span className="text-sm font-medium text-gray-900">{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full ${variants[variant]}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
