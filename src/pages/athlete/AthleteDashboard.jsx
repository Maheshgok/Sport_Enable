import Card from '../../components/common/Card'
import { getCurrentWeekProgress } from '../../data/mockAthleteCase'
import AssessmentScreen from './AssessmentScreen'
import RecommendationsScreen from './RecommendationsScreen'
import ProgressScreen from './ProgressScreen'

export default function AthleteDashboard({ currentView, setCurrentView }) {
  const currentWeek = getCurrentWeekProgress()

  // Dashboard view
  if (currentView === 'dashboard') {
    return (
      <div className="space-y-8">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Welcome Back, John</h2>
          <p className="text-gray-600">Here's your recovery status</p>
        </div>

        {/* Status Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <div className="text-sm text-gray-500 mb-2">Program Progress</div>
            <div className="text-3xl font-semibold text-gray-900">75%</div>
            <div className="text-sm text-gray-600 mt-2">On track</div>
          </Card>
          <Card>
            <div className="text-sm text-gray-500 mb-2">Pain Level</div>
            <div className="text-3xl font-semibold text-gray-900">{currentWeek.painLevel}/10</div>
            <div className="text-sm text-gray-600 mt-2">Improved</div>
          </Card>
          <Card>
            <div className="text-sm text-gray-500 mb-2">This Week</div>
            <div className="text-3xl font-semibold text-gray-900">{currentWeek.compliance}%</div>
            <div className="text-sm text-gray-600 mt-2">Compliance</div>
          </Card>
        </div>

        {/* Next Action */}
        <Card>
          <div className="flex items-start space-x-4">
            <div className="w-10 h-10 bg-gray-900 rounded-lg flex items-center justify-center text-white text-lg">
              ⚡
            </div>
            <div className="flex-1">
              <div className="text-sm text-gray-500 mb-1">Next Action</div>
              <h3 className="text-base font-medium text-gray-900 mb-2">Complete Today's Exercises</h3>
              <p className="text-sm text-gray-600 mb-4">
                You have 4 exercises scheduled for today. Start with your morning balance routine.
              </p>
              <button 
                onClick={() => setCurrentView('recommendations')}
                className="px-4 py-2 bg-gray-900 text-white rounded-md hover:bg-gray-800 text-sm"
              >
                View Exercise Plan
              </button>
            </div>
          </div>
        </Card>

        {/* Quick Links */}
        <div>
          <h3 className="text-base font-medium text-gray-900 mb-4">Quick Access</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <button
              onClick={() => setCurrentView('assessment')}
              className="p-6 bg-white border border-gray-200 rounded-lg text-left hover:border-gray-900"
            >
              <div className="text-2xl mb-3">📹</div>
              <div className="font-medium text-gray-900 mb-1">Movement Assessment</div>
              <div className="text-sm text-gray-600">Upload videos for analysis</div>
            </button>

            <button
              onClick={() => setCurrentView('recommendations')}
              className="p-6 bg-white border border-gray-200 rounded-lg text-left hover:border-gray-900"
            >
              <div className="text-2xl mb-3">💪</div>
              <div className="font-medium text-gray-900 mb-1">My Recommendations</div>
              <div className="text-sm text-gray-600">View insights & exercises</div>
            </button>

            <button
              onClick={() => setCurrentView('progress')}
              className="p-6 bg-white border border-gray-200 rounded-lg text-left hover:border-gray-900"
            >
              <div className="text-2xl mb-3">📈</div>
              <div className="font-medium text-gray-900 mb-1">Track Progress</div>
              <div className="text-sm text-gray-600">See your improvements</div>
            </button>
          </div>
        </div>

        {/* Recent Updates */}
        <Card title="Recent Updates">
          <div className="space-y-3">
            <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
              <span className="text-lg">✓</span>
              <div>
                <div className="font-medium text-gray-900">Pain Level Decreased</div>
                <div className="text-sm text-gray-600">Down to {currentWeek.painLevel}/10 this week</div>
                <div className="text-xs text-gray-500 mt-1">2 days ago</div>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
              <span className="text-xl">💡</span>
              <div>
                <div className="font-medium text-gray-900">New Insight Available</div>
                <div className="text-sm text-gray-600">Balance test shows 87% improvement</div>
                <div className="text-xs text-gray-500 mt-1">5 days ago</div>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
              <span className="text-xl">🎯</span>
              <div>
                <div className="font-medium text-gray-900">Week 4 Completed</div>
                <div className="text-sm text-gray-600">100% compliance - great work!</div>
                <div className="text-xs text-gray-500 mt-1">1 week ago</div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    )
  }

  // Other screens - Assessment, Recommendations, Progress
  if (currentView === 'assessment') {
    return (
      <div>
        <button
          onClick={() => setCurrentView('dashboard')}
          className="mb-4 flex items-center space-x-2 text-gray-900 hover:text-gray-700 font-medium"
        >
          <span>←</span>
          <span>Back to Dashboard</span>
        </button>
        <AssessmentScreen />
      </div>
    )
  }

  if (currentView === 'recommendations') {
    return (
      <div>
        <button
          onClick={() => setCurrentView('dashboard')}
          className="mb-4 flex items-center space-x-2 text-gray-900 hover:text-gray-700 font-medium"
        >
          <span>←</span>
          <span>Back to Dashboard</span>
        </button>
        <RecommendationsScreen />
      </div>
    )
  }

  if (currentView === 'progress') {
    return (
      <div>
        <button
          onClick={() => setCurrentView('dashboard')}
          className="mb-4 flex items-center space-x-2 text-gray-900 hover:text-gray-700 font-medium"
        >
          <span>←</span>
          <span>Back to Dashboard</span>
        </button>
        <ProgressScreen />
      </div>
    )
  }

  // Default to dashboard if view is unknown
  return null
}
