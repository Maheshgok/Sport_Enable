import { useState } from 'react'
import MainLayout from './components/layout/MainLayout'
import AthleteDashboard from './pages/athlete/AthleteDashboard'
import PhysiotherapistDashboard from './pages/physiotherapist/PhysiotherapistDashboard'
import CoachDashboard from './pages/coach/CoachDashboard'
import CaretakerDashboard from './pages/caretaker/CaretakerDashboard'
import VideoAnalysisTool from './pages/VideoAnalysisTool'

function App() {
  // Simple role state - in production, this would come from auth
  const [currentRole, setCurrentRole] = useState('athlete')
  const [currentView, setCurrentView] = useState('dashboard')

  // Reset view when role changes
  const handleRoleChange = (newRole) => {
    setCurrentRole(newRole)
    setCurrentView('dashboard')
  }

  const renderDashboard = () => {
    // Check if viewing the video analysis tool
    if (currentView === 'video-analysis') {
      return <VideoAnalysisTool />
    }

    switch (currentRole) {
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
      currentRole={currentRole} 
      onRoleChange={handleRoleChange}
      currentView={currentView}
      onViewChange={setCurrentView}
    >
      {renderDashboard()}
    </MainLayout>
  )
}

export default App
