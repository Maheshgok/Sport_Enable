import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'

export default function GoogleLogin() {
  const { signInWithGoogle } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGoogleSignIn = async () => {
    setError('')
    setLoading(true)
    try {
      await signInWithGoogle()
    } catch (err) {
      setError('Sign-in failed. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo / Brand */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Moove</h1>
          <p className="text-gray-500 text-base">
            AI-powered sports performance &amp; injury management
          </p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-1">Welcome</h2>
          <p className="text-sm text-gray-500 mb-8">
            Sign in to access your dashboard. New users will be guided through onboarding.
          </p>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <button
            onClick={handleGoogleSignIn}
            disabled={loading}
            className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 hover:border-gray-400 transition-colors disabled:opacity-60 disabled:cursor-not-allowed shadow-sm"
          >
            {/* Google icon */}
            <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            {loading ? 'Signing in…' : 'Continue with Google'}
          </button>

          <p className="mt-6 text-xs text-center text-gray-400">
            By signing in, you agree to our Terms of Service and Privacy Policy.
            <br />New sign-ups require admin approval before access is granted.
          </p>
        </div>

        {/* Features hint */}
        <div className="mt-8 grid grid-cols-3 gap-4 text-center">
          {[
            { icon: '🏃', label: 'Athletes' },
            { icon: '🏥', label: 'Physiotherapists' },
            { icon: '🎯', label: 'Coaches' },
          ].map((item) => (
            <div key={item.label} className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="text-2xl mb-1">{item.icon}</div>
              <div className="text-xs text-gray-500 font-medium">{item.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
