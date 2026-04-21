import { useAuth } from '../../context/AuthContext'

export default function Topbar({ currentRole }) {
  const { user, userProfile, logout } = useAuth()
  const displayName = userProfile?.displayName || user?.displayName || ''
  const email = user?.email || ''
  const photoURL = userProfile?.photoURL || user?.photoURL
  const roleLabel = currentRole ? currentRole.charAt(0).toUpperCase() + currentRole.slice(1) : ''

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-semibold text-gray-900">Moove</h1>
          {roleLabel && (
            <span className="px-2.5 py-0.5 bg-gray-100 text-gray-600 text-xs font-medium rounded-full">
              {roleLabel}
            </span>
          )}
        </div>

        <div className="flex items-center space-x-4">
          {/* User Info */}
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">{displayName}</div>
              <div className="text-xs text-gray-500">{email}</div>
            </div>
            {photoURL ? (
              <img src={photoURL} alt="" className="w-9 h-9 rounded-full" />
            ) : (
              <div className="w-9 h-9 bg-gray-900 rounded-full flex items-center justify-center text-white text-sm font-medium">
                {displayName?.[0]?.toUpperCase() || '?'}
              </div>
            )}
          </div>
          <button
            onClick={logout}
            className="text-sm text-gray-400 hover:text-gray-700 transition-colors"
            title="Sign out"
          >
            Sign out
          </button>
        </div>
      </div>
    </div>
  )
}
