import Card from '../../components/common/Card'
import Badge from '../../components/common/Badge'
import ProgressBar from '../../components/common/ProgressBar'

export default function AthleteOverview({ athletes, onSelectAthlete }) {
  const getStatusVariant = (status) => {
    switch (status) {
      case 'active':
        return 'active'
      case 'recovering':
        return 'warning'
      case 'cleared':
        return 'success'
      default:
        return 'default'
    }
  }

  const getTrainingStatusVariant = (status) => {
    switch (status) {
      case 'Full training':
        return 'success'
      case 'Modified training':
        return 'warning'
      case 'Rest':
        return 'warning'
      default:
        return 'info'
    }
  }

  const getTrainingStatusIcon = (status) => {
    switch (status) {
      case 'Full training':
        return '✅'
      case 'Modified training':
        return '⚠️'
      case 'Rest':
        return '🛑'
      default:
        return '📋'
    }
  }

  // Group athletes by status
  const activeAthletes = athletes.filter(a => a.status === 'active')
  const recoveringAthletes = athletes.filter(a => a.status === 'recovering')
  const clearedAthletes = athletes.filter(a => a.status === 'cleared')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Athlete Overview</h2>
        <p className="text-gray-500">Monitor recovery and training status</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="text-sm text-gray-500 mb-1">Total Athletes</div>
          <div className="text-3xl font-semibold text-gray-900">{athletes.length}</div>
        </Card>
        <Card>
          <div className="text-sm text-gray-500 mb-1">Full Training</div>
          <div className="text-3xl font-semibold text-gray-900">
            {athletes.filter(a => a.trainingStatus === 'Full training').length}
          </div>
        </Card>
        <Card>
          <div className="text-sm text-gray-500 mb-1">Modified Training</div>
          <div className="text-3xl font-semibold text-gray-900">
            {athletes.filter(a => a.trainingStatus === 'Modified training').length}
          </div>
        </Card>
        <Card>
          <div className="text-sm text-gray-500 mb-1">On Rest</div>
          <div className="text-3xl font-semibold text-gray-900">
            {athletes.filter(a => a.trainingStatus === 'Rest').length}
          </div>
        </Card>
      </div>

      {/* Active Training Athletes */}
      {activeAthletes.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center space-x-2">
            <span>✅</span>
            <span>Active Training ({activeAthletes.length})</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {activeAthletes.map((athlete) => (
              <Card key={athlete.id}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center text-white font-bold">
                      {athlete.avatar}
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{athlete.name}</h4>
                      <p className="text-sm text-gray-500">{athlete.sport} - {athlete.position}</p>
                    </div>
                  </div>
                  <Badge variant={getStatusVariant(athlete.status)}>
                    {athlete.status}
                  </Badge>
                </div>

                <div className="space-y-2 mb-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Condition:</span>
                    <span className="text-gray-900">{athlete.condition.substring(0, 30)}...</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Training Status:</span>
                    <Badge variant={getTrainingStatusVariant(athlete.trainingStatus)}>
                      {getTrainingStatusIcon(athlete.trainingStatus)} {athlete.trainingStatus}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Recovery:</span>
                    <span className="font-medium text-gray-900">{athlete.recoveryProgress}%</span>
                  </div>
                </div>

                <div className="mb-3">
                  <ProgressBar value={athlete.recoveryProgress} variant="success" />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Next: {athlete.nextSession}</span>
                  <button
                    onClick={() => onSelectAthlete(athlete.id)}
                    className="px-3 py-1 bg-gray-900 text-white rounded text-sm hover:bg-gray-800 transition-colors"
                  >
                    View Details →
                  </button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Recovering Athletes */}
      {recoveringAthletes.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center space-x-2">
            <span>🏥</span>
            <span>In Recovery ({recoveringAthletes.length})</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recoveringAthletes.map((athlete) => (
              <Card key={athlete.id}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center text-white font-bold">
                      {athlete.avatar}
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{athlete.name}</h4>
                      <p className="text-sm text-gray-500">{athlete.sport} - {athlete.position}</p>
                    </div>
                  </div>
                  <Badge variant={getStatusVariant(athlete.status)}>
                    {athlete.status}
                  </Badge>
                </div>

                <div className="space-y-2 mb-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Condition:</span>
                    <span className="text-gray-900">{athlete.condition.substring(0, 30)}...</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Training Status:</span>
                    <Badge variant={getTrainingStatusVariant(athlete.trainingStatus)}>
                      {getTrainingStatusIcon(athlete.trainingStatus)} {athlete.trainingStatus}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Recovery:</span>
                    <span className="font-medium text-gray-900">{athlete.recoveryProgress}%</span>
                  </div>
                </div>

                <div className="mb-3">
                  <ProgressBar value={athlete.recoveryProgress} variant="warning" />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Status: {athlete.nextSession}</span>
                  <button
                    onClick={() => onSelectAthlete(athlete.id)}
                    className="px-3 py-1 bg-gray-900 text-white rounded text-sm hover:bg-gray-800 transition-colors"
                  >
                    View Details →
                  </button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Cleared Athletes */}
      {clearedAthletes.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center space-x-2">
            <span>🎉</span>
            <span>Cleared for Full Training ({clearedAthletes.length})</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {clearedAthletes.map((athlete) => (
              <Card key={athlete.id}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center text-white font-bold">
                      {athlete.avatar}
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{athlete.name}</h4>
                      <p className="text-sm text-gray-500">{athlete.sport} - {athlete.position}</p>
                    </div>
                  </div>
                  <Badge variant={getStatusVariant(athlete.status)}>
                    ✓ {athlete.status}
                  </Badge>
                </div>

                <div className="bg-gray-50 border border-gray-200 p-3 rounded-lg mb-3">
                  <p className="text-sm text-gray-900">{athlete.condition}</p>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Next session: {athlete.nextSession}</span>
                  <button
                    onClick={() => onSelectAthlete(athlete.id)}
                    className="px-3 py-1 bg-gray-900 text-white rounded text-sm hover:bg-gray-800 transition-colors"
                  >
                    View Details →
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
