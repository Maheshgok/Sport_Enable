import Card from '../../components/common/Card'
import Badge from '../../components/common/Badge'
import ProgressBar from '../../components/common/ProgressBar'

export default function CaseList({ cases, onSelectCase }) {
  const getStatusVariant = (status) => {
    switch (status) {
      case 'active':
        return 'active'
      case 'assessment':
        return 'new'
      case 'completed':
        return 'default'
      default:
        return 'default'
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'text-red-500'
      case 'normal':
        return 'text-blue-500'
      case 'low':
        return 'text-gray-500'
      default:
        return 'text-gray-500'
    }
  }

  const activeCases = cases.filter(c => c.status !== 'completed')
  const completedCases = cases.filter(c => c.status === 'completed')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Athlete Cases</h2>
        <p className="text-gray-500">Manage your patient assessments and treatments</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <div className="text-sm text-gray-500 mb-1">Active Cases</div>
          <div className="text-3xl font-semibold text-gray-900">
            {activeCases.length}
          </div>
        </Card>
        <Card>
          <div className="text-sm text-gray-500 mb-1">Pending Assessment</div>
          <div className="text-3xl font-semibold text-gray-900">
            {cases.filter(c => c.status === 'assessment').length}
          </div>
        </Card>
        <Card>
          <div className="text-sm text-gray-500 mb-1">Completed</div>
          <div className="text-3xl font-semibold text-gray-900">
            {completedCases.length}
          </div>
        </Card>
      </div>

      {/* Active Cases */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Active Cases</h3>
        <div className="space-y-3">
          {activeCases.map((athleteCase) => (
            <Card key={athleteCase.id}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 flex-1">
                  {/* Avatar */}
                  <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                    {athleteCase.athlete.avatar}
                  </div>

                  {/* Info */}
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-1">
                      <h4 className="font-semibold text-gray-900">{athleteCase.athlete.name}</h4>
                      <Badge variant={getStatusVariant(athleteCase.status)}>
                        {athleteCase.status}
                      </Badge>
                      {athleteCase.priority === 'high' && (
                        <Badge variant="warning">High Priority</Badge>
                      )}
                    </div>
                    <div className="text-sm text-gray-600">{athleteCase.condition}</div>
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span>🏃 {athleteCase.athlete.sport}</span>
                      <span>📅 Assigned: {athleteCase.assignedDate}</span>
                      <span>🔄 Last update: {athleteCase.lastUpdate}</span>
                    </div>
                  </div>

                  {/* Progress */}
                  <div className="text-right mr-4 min-w-[120px]">
                    <div className="text-sm text-gray-500 mb-1">Progress</div>
                    <div className="text-2xl font-semibold text-gray-900 mb-2">{athleteCase.progress}%</div>
                    <ProgressBar value={athleteCase.progress} variant="success" />
                  </div>
                </div>

                {/* Action Button */}
                <button
                  onClick={() => onSelectCase(athleteCase.id)}
                  className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors text-sm font-medium"
                >
                  View Case →
                </button>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Completed Cases */}
      {completedCases.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Completed Cases</h3>
          <div className="space-y-3">
            {completedCases.map((athleteCase) => (
              <Card key={athleteCase.id}>
                <div className="flex items-center justify-between opacity-75">
                  <div className="flex items-center space-x-4 flex-1">
                    <div className="w-12 h-12 bg-gray-400 rounded-full flex items-center justify-center text-white font-bold">
                      {athleteCase.athlete.avatar}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-1">
                        <h4 className="font-semibold text-gray-900">{athleteCase.athlete.name}</h4>
                        <Badge variant="default">
                          ✓ {athleteCase.status}
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-600">{athleteCase.condition}</div>
                    </div>
                  </div>
                  <button
                    onClick={() => onSelectCase(athleteCase.id)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
                  >
                    View
                  </button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
