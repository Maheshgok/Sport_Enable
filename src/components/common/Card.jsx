export default function Card({ title, children, className = '' }) {
  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
      {title && <h3 className="text-base font-medium text-gray-900 mb-4 pb-3 border-b border-gray-100">{title}</h3>}
      {children}
    </div>
  )
}
