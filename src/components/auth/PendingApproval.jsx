import { useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'

const ROLE_LABELS = {
  athlete: 'Athlete',
  physiotherapist: 'Physiotherapist',
  coach: 'Coach',
  caretaker: 'Caretaker',
}

export default function PendingApproval() {
  const { user, userProfile, logout, refreshProfile } = useAuth()

  // Poll for approval every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      refreshProfile()
    }, 30000)
    return () => clearInterval(interval)
  }, [refreshProfile])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md text-center">
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-10">
          {/* Icon */}
          <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-5">
            <svg className="w-8 h-8 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>

          <h2 className="text-xl font-semibold text-gray-900 mb-2">Awaiting Approval</h2>
          <p className="text-gray-500 text-sm mb-6">
            Your access request has been submitted. An admin will review it shortly and you'll be notified when approved.
          </p>

          {/* Submitted details */}
          <div className="bg-gray-50 rounded-xl p-4 text-left space-y-3 mb-6">
            <div className="flex items-center gap-3">
              {user?.photoURL ? (
                <img src={user.photoURL} alt="" className="w-9 h-9 rounded-full" />
              ) : (
                <div className="w-9 h-9 bg-gray-200 rounded-full flex items-center justify-center text-gray-600 text-sm font-medium">
                  {user?.displayName?.[0]}
                </div>
              )}
              <div>
                <div className="text-sm font-medium text-gray-900">{userProfile?.displayName || user?.displayName}</div>
                <div className="text-xs text-gray-500">{user?.email}</div>
              </div>
            </div>
            <div className="border-t border-gray-200 pt-3 grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-gray-400">Requested role</span>
                <div className="font-medium text-gray-700 mt-0.5">
                  {ROLE_LABELS[userProfile?.role] || userProfile?.role}
                </div>
              </div>
              {userProfile?.sport && (
                <div>
                  <span className="text-gray-400">Sport</span>
                  <div className="font-medium text-gray-700 mt-0.5">{userProfile.sport}</div>
                </div>
              )}
              {userProfile?.specialization && (
                <div>
                  <span className="text-gray-400">Specialization</span>
                  <div className="font-medium text-gray-700 mt-0.5">{userProfile.specialization}</div>
                </div>
              )}
              {userProfile?.phone && (
                <div>
                  <span className="text-gray-400">Phone</span>
                  <div className="font-medium text-gray-700 mt-0.5">{userProfile.phone}</div>
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center justify-center gap-2 text-xs text-gray-400 mb-6">
            <div className="w-1.5 h-1.5 bg-amber-400 rounded-full animate-pulse"></div>
            Checking for approval updates every 30 seconds…
          </div>

          <button
            onClick={logout}
            className="text-sm text-gray-400 hover:text-gray-700 underline"
          >
            Sign out
          </button>
        </div>

        <p className="mt-4 text-xs text-gray-400">
          Having trouble? Contact <span className="text-gray-600">support@moove.ai</span>
        </p>
      </div>
    </div>
  )
}
