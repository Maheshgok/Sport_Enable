import Card from '../../components/common/Card'
import Badge from '../../components/common/Badge'
import ProgressBar from '../../components/common/ProgressBar'
import { progress } from '../../data/mockAthleteCase'

export default function ProgressScreen() {
  const { weeklyMetrics, improvements, overallProgress } = progress

  // Get completed weeks only
  const completedWeeks = weeklyMetrics.filter(week => week.completed)
  const currentWeek = weeklyMetrics.find(week => !week.completed) || weeklyMetrics[weeklyMetrics.length - 1]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800">Your Progress</h2>
        <p className="text-gray-600">Track your recovery and improvements</p>
      </div>

      {/* Overall Progress */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <div className="text-sm text-gray-500">Overall Progress</div>
              <Badge variant="improving">Improving</Badge>
            </div>
            <div className="text-3xl font-semibold text-gray-900">{overallProgress}%</div>
          </div>
          <div className="text-4xl">📈</div>
        </div>
        <ProgressBar value={overallProgress} variant="success" />
        <p className="text-xs text-gray-500 mt-2">
          {100 - overallProgress}% remaining to complete program
        </p>
      </Card>

      {/* Current Week Stats */}
      <Card title="This Week">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="text-2xl font-semibold text-gray-900">{currentWeek.compliance}%</div>
            <div className="text-sm text-gray-600 mt-1">Compliance</div>
            <Badge variant="success" className="mt-2">On Track</Badge>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="text-2xl font-semibold text-gray-900">{currentWeek.painLevel}/10</div>
            <div className="text-sm text-gray-600 mt-1">Pain Level</div>
            <Badge variant="improving" className="mt-2">Improving</Badge>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="text-2xl font-semibold text-gray-900">{currentWeek.energyLevel}/10</div>
            <div className="text-sm text-gray-600 mt-1">Energy Level</div>
            <Badge variant="success" className="mt-2">Good</Badge>
          </div>
        </div>
      </Card>

      {/* Performance Improvements */}
      <div>
        <h3 className="text-base font-medium text-gray-900 mb-4">Key Improvements</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(improvements).map(([key, value]) => (
            <Card key={key}>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-500 capitalize">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </div>
                  <Badge variant="improving">+{value.improvement}</Badge>
                </div>
                <div className="flex items-baseline space-x-2">
                  <span className="text-2xl font-semibold text-gray-900">{value.current}</span>
                  <span className="text-sm text-gray-500">/ {value.target}</span>
                  <span className="text-xs text-gray-400">{value.unit}</span>
                </div>
                <ProgressBar 
                  value={parseFloat(value.current)} 
                  max={parseFloat(value.target)} 
                  variant="success"
                />
                <div className="text-xs text-gray-500">from {value.baseline} {value.unit}</div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Weekly History */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-3">📅 Weekly History</h3>
        <Card>
          <div className="space-y-3">
            {weeklyMetrics.slice().reverse().map((week) => (
              <div 
                key={week.week}
                className={`p-4 rounded-lg border ${
                  !week.completed 
                    ? 'bg-blue-50 border-blue-200' 
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <span className="font-semibold text-gray-800">Week {week.week}</span>
                    <span className="text-sm text-gray-500">{week.date}</span>
                    {!week.completed && (
                      <span className="px-2 py-1 bg-blue-500 text-white rounded text-xs font-medium">
                        Current
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    {week.completed && (
                      <span className="text-green-500 text-xl">✓</span>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Compliance: </span>
                    <span className={`font-medium ${
                      week.compliance >= 90 ? 'text-green-600' :
                      week.compliance >= 70 ? 'text-blue-600' :
                      'text-orange-600'
                    }`}>
                      {week.compliance}%
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Pain: </span>
                    <span className={`font-medium ${
                      week.painLevel === 0 ? 'text-green-600' :
                      week.painLevel <= 2 ? 'text-blue-600' :
                      'text-orange-600'
                    }`}>
                      {week.painLevel}/10
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Energy: </span>
                    <span className="font-medium text-gray-800">{week.energyLevel}/10</span>
                  </div>
                </div>

                {week.notes && (
                  <div className="mt-2 text-sm text-gray-600 italic">
                    "{week.notes}"
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Summary Card */}
      <Card>
        <div className="flex items-start space-x-3">
          <div className="text-2xl">✨</div>
          <div>
            <div className="font-medium text-gray-800 mb-1">Keep Up the Great Work!</div>
            <p className="text-sm text-gray-600">
              You've completed {completedWeeks.length} weeks of your program. 
              Pain has reduced from 2/10 to {currentWeek.painLevel}/10, and your balance 
              has improved by 87%. Stay consistent!
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}
