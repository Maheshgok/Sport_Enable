import Card from '../../components/common/Card'
import Badge from '../../components/common/Badge'
import ProgressBar from '../../components/common/ProgressBar'

export default function Monitoring({ athlete, alerts, weeklyCompliance }) {
  if (!athlete) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Monitoring</h2>
          <p className="text-gray-500">No athlete selected</p>
        </div>
      </div>
    )
  }

  const getAlertIcon = (type) => {
    switch (type) {
      case 'warning':
        return '⚠️'
      case 'success':
        return '✅'
      case 'info':
        return 'ℹ️'
      case 'reminder':
        return '🔔'
      default:
        return '📋'
    }
  }

  const getAlertVariant = (type) => {
    switch (type) {
      case 'warning':
        return 'warning'
      case 'success':
        return 'success'
      case 'info':
        return 'info'
      case 'reminder':
        return 'info'
      default:
        return 'default'
    }
  }

  const getAlertColor = (type) => {
    switch (type) {
      case 'warning':
        return 'border-l-4 border-l-gray-900'
      case 'success':
        return 'border-l-4 border-l-gray-900'
      case 'info':
        return 'border-l-4 border-l-gray-900'
      case 'reminder':
        return 'border-l-4 border-l-gray-900'
      default:
        return 'border-l-4 border-l-gray-900'
    }
  }

  const averageCompliance = weeklyCompliance 
    ? Math.round(weeklyCompliance.reduce((sum, day) => sum + day.compliance, 0) / weeklyCompliance.length)
    : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Monitoring - {athlete.name}</h2>
        <p className="text-gray-500">Track compliance and stay updated</p>
      </div>

      {/* Compliance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <div className="text-sm text-gray-500 mb-1">Current Compliance</div>
          <div className="text-4xl font-semibold text-gray-900 mb-2">{athlete.compliance}%</div>
          <Badge variant={
            athlete.compliance >= 90 ? 'success' :
            athlete.compliance >= 70 ? 'info' :
            'warning'
          }>
            {athlete.compliance >= 90 ? '✓ Excellent' :
             athlete.compliance >= 70 ? '⚠ Good' :
             '⚠️ Needs Attention'}
          </Badge>
        </Card>

        <Card>
          <div className="text-sm text-gray-500 mb-1">Weekly Average</div>
          <div className="text-4xl font-semibold text-gray-900 mb-2">{averageCompliance}%</div>
          <div className="text-sm text-gray-600">Last 7 days</div>
        </Card>
      </div>

      {/* Weekly Compliance Chart */}
      {weeklyCompliance && (
        <Card title="Weekly Compliance">
          <div className="grid grid-cols-7 gap-2">
            {weeklyCompliance.map((day, index) => (
              <div key={index} className="text-center">
                <div className="text-xs text-gray-600 mb-2">{day.day}</div>
                <div className="relative h-32 bg-gray-100 rounded">
                  <div 
                    className="absolute bottom-0 w-full rounded transition-all bg-gray-900"
                    style={{ height: `${day.compliance}%` }}
                  />
                </div>
                <div className="text-xs font-medium text-gray-700 mt-2">
                  {day.compliance}%
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Alerts & Notifications */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">🔔 Alerts & Notifications</h3>
        
        {alerts && alerts.length > 0 ? (
          <div className="space-y-3">
            {alerts.map((alert) => (
              <Card key={alert.id} className={getAlertColor(alert.type)}>
                <div className="flex items-start space-x-3">
                  <div className="text-2xl">{getAlertIcon(alert.type)}</div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <Badge variant={getAlertVariant(alert.type)}>
                        {alert.type}
                      </Badge>
                      <span className="text-xs text-gray-500">{alert.time}</span>
                    </div>
                    <p className="text-sm text-gray-900">{alert.message}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <div className="text-center py-6 text-gray-500">
              <div className="text-3xl mb-2">🔕</div>
              <div className="text-sm">No alerts at this time</div>
            </div>
          </Card>
        )}
      </div>

      {/* Quick Stats */}
      <Card title="Today's Stats">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
            <div className="text-2xl mb-1">💪</div>
            <div className="text-xs text-gray-500">Exercise Sessions</div>
            <div className="text-lg font-semibold text-gray-900">6</div>
          </div>
          <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
            <div className="text-2xl mb-1">🍽️</div>
            <div className="text-xs text-gray-500">Meals Provided</div>
            <div className="text-lg font-semibold text-gray-900">3</div>
          </div>
          <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
            <div className="text-2xl mb-1">🏥</div>
            <div className="text-xs text-gray-500">Care Tasks</div>
            <div className="text-lg font-semibold text-gray-900">2</div>
          </div>
        </div>
      </Card>

      {/* Status Summary */}
      <Card>
        <div className="flex items-start space-x-3">
          <div className="text-2xl">📊</div>
          <div>
            <div className="font-medium text-gray-900 mb-1">Overall Status</div>
            <p className="text-sm text-gray-600">
              {athlete.status === 'active' 
                ? 'Athlete is progressing well with their recovery plan. Continue monitoring compliance and addressing any concerns promptly.'
                : athlete.status === 'recovering'
                ? 'Athlete is in active recovery phase. Close monitoring required. Follow all care protocols carefully.'
                : 'Athlete status is stable. Maintain current care routine.'}
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}
