import { useState } from 'react'
import { useAuth } from './context/AuthContext'
import GoogleLogin from './components/auth/GoogleLogin'
import CompleteProfile from './components/auth/CompleteProfile'
import PendingApproval from './components/auth/PendingApproval'
import SuperAdminDashboard from './pages/superadmin/SuperAdminDashboard'
import MainLayout from './components/layout/MainLayout'
import AthleteDashboard from './pages/athlete/AthleteDashboard'
import PhysiotherapistDashboard from './pages/physiotherapist/PhysiotherapistDashboard'
import CoachDashboard from './pages/coach/CoachDashboard'
import CaretakerDashboard from './pages/caretaker/CaretakerDashboard'
import VideoAnalysisTool from './pages/VideoAnalysisTool'
import LandingPage from './pages/LandingPage'
import { Routes, Route } from 'react-router-dom'

function RejectedScreen() {
  const { logout, userProfile } = useAuth()
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md text-center bg-white rounded-2xl border border-gray-200 shadow-sm p-10">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-5">
          <svg className="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Not Approved</h2>
        <p className="text-gray-500 text-sm mb-4">
          Your access request was not approved.
          {userProfile?.reviewNote && (
            <span className="block mt-2 text-gray-600 italic">"{userProfile.reviewNote}"</span>
          )}
        </p>
        <p className="text-sm text-gray-400 mb-6">Contact <span className="text-gray-600">support@moove.ai</span> for assistance.</p>
        <button onClick={logout} className="px-6 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800">
          Sign out
        </button>
      </div>
    </div>
  )
}

function LoadingScreen() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-10 h-10 border-2 border-gray-900 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        <p className="text-sm text-gray-500">Loading…</p>
      </div>
    </div>
  )
}

function MainApp() {
  const { userProfile } = useAuth()
  const [currentView, setCurrentView] = useState('dashboard')
  const role = userProfile.role

  const renderDashboard = () => {
    if (currentView === 'video-analysis') return <VideoAnalysisTool />
    switch (role) {
      case 'athlete':
        return <AthleteDashboard currentView={currentView} setCurrentView={setCurrentView} />
      case 'physiotherapist':
        return <PhysiotherapistDashboard currentView={currentView} setCurrentView={setCurrentView} />
      case 'coach':
        return <CoachDashboard currentView={currentView} setCurrentView={setCurrentView} />
      case 'caretaker':
        return <CaretakerDashboard currentView={currentView} setCurrentView={setCurrentView} />
      default:
        return <AthleteDashboard currentView={currentView} setCurrentView={setCurrentView} />
    }
  }

  return (
    <MainLayout
      currentRole={role}
      currentView={currentView}
      onViewChange={setCurrentView}
    >
      {renderDashboard()}
    </MainLayout>
  )
}

function MooveApp() {
  const { user, userProfile, loading } = useAuth()

  if (loading) return <LoadingScreen />
  if (!user) return <GoogleLogin />
  if (!userProfile) return <CompleteProfile />

  if (userProfile.status === 'pending') return <PendingApproval />
  if (userProfile.status === 'rejected') return <RejectedScreen />
  if (userProfile.role === 'superadmin') return <SuperAdminDashboard />

  return <MainApp />
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/moove/*" element={<MooveApp />} />
    </Routes>
  )
}

export default App
