import { useState } from 'react'
import Card from '../../components/common/Card'
import AthleteOverview from './AthleteOverview'
import AthleteDetail from './AthleteDetail'
import { coachAthletes, athleteDetails } from '../../data/mockCoachData'

export default function CoachDashboard({ currentView, setCurrentView }) {
  const [internalView, setInternalView] = useState('overview') // 'overview' or 'detail'
  const [selectedAthleteId, setSelectedAthleteId] = useState(null)
  
  // Local state for athlete data and comments
  const [athletes] = useState(coachAthletes)
  const [details, setDetails] = useState(athleteDetails)

  const handleSelectAthlete = (athleteId) => {
    setSelectedAthleteId(athleteId)
    setInternalView('detail')
  }

  const handleBackToOverview = () => {
    setInternalView('overview')
    setSelectedAthleteId(null)
  }

  const handleAddComment = (athleteId, commentText) => {
    const newComment = {
      id: `COM${Date.now()}`,
      author: 'Mike Coach',
      date: new Date().toISOString().split('T')[0],
      text: commentText
    }

    setDetails(prev => ({
      ...prev,
      [athleteId]: {
        ...prev[athleteId],
        comments: [...(prev[athleteId]?.comments || []), newComment]
      }
    }))
  }

  const selectedAthlete = athletes.find(a => a.id === selectedAthleteId)
  const selectedDetails = details[selectedAthleteId]

  // Dashboard view
  if (currentView === 'dashboard') {
    const activeTraining = athletes.filter(a => a.trainingStatus === 'active').length
    const inRecovery = athletes.filter(a => a.trainingStatus === 'recovery').length
    const avgProgress = Math.round(athletes.reduce((sum, a) => sum + a.recoveryProgress, 0) / athletes.length)

    return (
      <div className="space-y-8">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Coach Dashboard</h2>
          <p className="text-gray-600">Monitor your athletes' recovery and training</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <div className="text-sm text-gray-500 mb-2">Active Training</div>
            <div className="text-3xl font-semibold text-gray-900">{activeTraining}</div>
          </Card>
          <Card>
            <div className="text-sm text-gray-500 mb-2">In Recovery</div>
            <div className="text-3xl font-semibold text-gray-900">{inRecovery}</div>
          </Card>
          <Card>
            <div className="text-sm text-gray-500 mb-2">Avg Progress</div>
            <div className="text-3xl font-semibold text-gray-900">{avgProgress}%</div>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card title="Quick Actions">
          <div className="grid grid-cols-2 gap-6">
            <button
              onClick={() => setCurrentView('athletes')}
              className="p-6 bg-white border border-gray-200 rounded-lg text-left hover:border-gray-900"
            >
              <div className="text-2xl mb-3">🏃</div>
              <div className="font-medium text-gray-900 mb-1">View Athletes</div>
              <div className="text-sm text-gray-600">Monitor recovery status</div>
            </button>
            <button
              className="p-6 bg-white border border-gray-200 rounded-lg text-left hover:border-gray-900"
            >
              <div className="text-2xl mb-3">📈</div>
              <div className="font-medium text-gray-900 mb-1">Analytics</div>
              <div className="text-sm text-gray-600">View team performance</div>
            </button>
          </div>
        </Card>
      </div>
    )
  }

  // Athletes view
  if (currentView === 'athletes') {
    return (
      <div>
        {internalView === 'overview' ? (
          <AthleteOverview 
            athletes={athletes}
            onSelectAthlete={handleSelectAthlete}
          />
        ) : (
          <AthleteDetail
            athlete={selectedAthlete}
            details={selectedDetails}
            onBack={handleBackToOverview}
            onAddComment={handleAddComment}
          />
        )}
      </div>
    )
  }
}
