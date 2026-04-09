import { useState } from 'react'
import Card from '../../components/common/Card'
import DailyPlan from './DailyPlan'
import Monitoring from './Monitoring'
import { assignedAthletes, dailyPlans, alerts, weeklyCompliance } from '../../data/mockCaretakerData'

export default function CaretakerDashboard({ currentView, setCurrentView }) {
  const [internalView, setInternalView] = useState('overview') // For athlete selection within views
  const [selectedAthleteId, setSelectedAthleteId] = useState(null)
  
  // Local state for daily plans (to track task completion)
  const [plans, setPlans] = useState(dailyPlans)

  const handleSelectAthlete = (athleteId, view) => {
    setSelectedAthleteId(athleteId)
    setInternalView(view)
    // Update the sidebar view as well
    if (view === 'dailyPlan') {
      setCurrentView('plans')
    } else if (view === 'monitoring') {
      setCurrentView('monitoring')
    }
  }

  const handleBackToOverview = () => {
    setInternalView('overview')
    setSelectedAthleteId(null)
    // Keep current sidebar view (don't navigate back to dashboard)
  }

  const handleToggleTask = (athleteId, taskId) => {
    setPlans(prev => ({
      ...prev,
      [athleteId]: {
        ...prev[athleteId],
        tasks: prev[athleteId].tasks.map(task =>
          task.id === taskId ? { ...task, completed: !task.completed } : task
        )
      }
    }))
  }

  const selectedAthlete = assignedAthletes.find(a => a.id === selectedAthleteId)

  // Dashboard (Overview) view
  if (currentView === 'dashboard') {
    return (
      <div className="space-y-8">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">Caretaker Dashboard</h2>
          <p className="text-gray-600">Manage daily care and monitor athletes</p>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <div className="text-sm text-gray-500 mb-2">Assigned Athletes</div>
            <div className="text-3xl font-semibold text-gray-900">{assignedAthletes.length}</div>
          </Card>
          <Card>
            <div className="text-sm text-gray-500 mb-2">Avg. Compliance</div>
            <div className="text-3xl font-semibold text-gray-900">
              {Math.round(assignedAthletes.reduce((sum, a) => sum + a.compliance, 0) / assignedAthletes.length)}%
            </div>
          </Card>
          <Card>
            <div className="text-sm text-gray-500 mb-2">Tasks Today</div>
            <div className="text-3xl font-semibold text-gray-900">
              {Object.values(plans).reduce((sum, plan) => sum + plan.tasks.length, 0)}
            </div>
          </Card>
        </div>

        {/* Athlete Cards */}
        <div>
          <h3 className="text-base font-medium text-gray-900 mb-4">Your Athletes</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {assignedAthletes.map((athlete) => {
              const athletePlan = plans[athlete.id]
              const completedTasks = athletePlan ? athletePlan.tasks.filter(t => t.completed).length : 0
              const totalTasks = athletePlan ? athletePlan.tasks.length : 0
              const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

              return (
                <Card key={athlete.id}>
                  <div className="flex items-center space-x-3 mb-3">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold ${
                      athlete.status === 'active' ? 'bg-green-500' : 'bg-orange-500'
                    }`}>
                      {athlete.avatar}
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800">{athlete.name}</h4>
                      <p className="text-sm text-gray-600">{athlete.sport}</p>
                    </div>
                  </div>

                  <div className="space-y-3 mb-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Today's Tasks:</span>
                      <span className="font-medium text-gray-900">
                        {completedTasks}/{totalTasks}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-gray-900 h-2 rounded-full"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Compliance:</span>
                      <span className="font-medium text-gray-900">
                        {athlete.compliance}%
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() => handleSelectAthlete(athlete.id, 'dailyPlan')}
                      className="px-3 py-2 bg-gray-900 text-white rounded-md hover:bg-gray-800 text-sm"
                    >
                      Daily Plan
                    </button>
                    <button
                      onClick={() => handleSelectAthlete(athlete.id, 'monitoring')}
                      className="px-3 py-2 border border-gray-300 text-gray-700 rounded-md hover:border-gray-900 text-sm"
                    >
                      Monitor
                    </button>
                  </div>
                </Card>
              )
            })}
          </div>
        </div>

        {/* Quick Overview */}
        <Card title="Today's Overview">
          <div className="space-y-2">
            {assignedAthletes.map((athlete) => {
              const athletePlan = plans[athlete.id]
              const pendingTasks = athletePlan ? athletePlan.tasks.filter(t => !t.completed && t.priority === 'high') : []
              
              return pendingTasks.length > 0 ? (
                <div key={athlete.id} className="p-3 bg-orange-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-medium text-gray-800">{athlete.name}</span>
                      <span className="text-sm text-gray-600 ml-2">
                        - {pendingTasks.length} high priority task{pendingTasks.length !== 1 ? 's' : ''} pending
                      </span>
                    </div>
                    <button
                      onClick={() => handleSelectAthlete(athlete.id, 'dailyPlan')}
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                    >
                      View →
                    </button>
                  </div>
                </div>
              ) : null
            })}
          </div>
        </Card>
      </div>
    )
  }

  // Daily Plans view
  if (currentView === 'plans') {
    if (internalView === 'dailyPlan' && selectedAthleteId) {
      return (
        <div>
          <button
            onClick={handleBackToOverview}
            className="mb-4 flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium"
          >
            <span>←</span>
            <span>Back to Athletes</span>
          </button>
          <DailyPlan 
            athleteId={selectedAthleteId}
            plan={plans[selectedAthleteId]}
            onToggleTask={handleToggleTask}
          />
        </div>
      )
    }

    // Show athlete selection
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Daily Plans</h2>
          <p className="text-gray-600">Select an athlete to view their daily tasks</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {assignedAthletes.map((athlete) => {
            const athletePlan = plans[athlete.id]
            const completedTasks = athletePlan ? athletePlan.tasks.filter(t => t.completed).length : 0
            const totalTasks = athletePlan ? athletePlan.tasks.length : 0
            const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

            return (
              <Card key={athlete.id}>
                <div className="flex items-center space-x-3 mb-3">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold ${
                    athlete.status === 'active' ? 'bg-green-500' : 'bg-orange-500'
                  }`}>
                    {athlete.avatar}
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-800">{athlete.name}</h4>
                    <p className="text-sm text-gray-600">{athlete.sport}</p>
                  </div>
                </div>
                <div className="space-y-2 mb-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Today's Tasks:</span>
                    <span className="font-medium text-gray-800">
                      {completedTasks}/{totalTasks}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
                <button
                  onClick={() => handleSelectAthlete(athlete.id, 'dailyPlan')}
                  className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  View Daily Plan
                </button>
              </Card>
            )
          })}
        </div>
      </div>
    )
  }

  // Monitoring view
  if (currentView === 'monitoring') {
    if (internalView === 'monitoring' && selectedAthleteId) {
      return (
        <div>
          <button
            onClick={handleBackToOverview}
            className="mb-4 flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium"
          >
            <span>←</span>
            <span>Back to Athletes</span>
          </button>
          <Monitoring
            athlete={selectedAthlete}
            alerts={alerts[selectedAthleteId]}
            weeklyCompliance={weeklyCompliance[selectedAthleteId]}
          />
        </div>
      )
    }

    // Show athlete selection
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Monitoring</h2>
          <p className="text-gray-600">Select an athlete to view their compliance and alerts</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {assignedAthletes.map((athlete) => (
            <Card key={athlete.id}>
              <div className="flex items-center space-x-3 mb-3">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold ${
                  athlete.status === 'active' ? 'bg-green-500' : 'bg-orange-500'
                }`}>
                  {athlete.avatar}
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800">{athlete.name}</h4>
                  <p className="text-sm text-gray-600">{athlete.sport}</p>
                </div>
              </div>
              <div className="space-y-2 mb-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Compliance:</span>
                  <span className={`font-medium ${
                    athlete.compliance >= 90 ? 'text-green-600' :
                    athlete.compliance >= 70 ? 'text-blue-600' :
                    'text-orange-600'
                  }`}>
                    {athlete.compliance}%
                  </span>
                </div>
              </div>
              <button
                onClick={() => handleSelectAthlete(athlete.id, 'monitoring')}
                className="w-full px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
              >
                View Monitoring
              </button>
            </Card>
          ))}
        </div>
      </div>
    )
  }
}