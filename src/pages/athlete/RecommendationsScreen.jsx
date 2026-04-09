import Card from '../../components/common/Card'
import Badge from '../../components/common/Badge'
import { insights, plan } from '../../data/mockAthleteCase'

export default function RecommendationsScreen() {
  // Group exercises by category
  const exercisesByCategory = plan.exercises.reduce((acc, exercise) => {
    if (!acc[exercise.category]) {
      acc[exercise.category] = []
    }
    acc[exercise.category].push(exercise)
    return acc
  }, {})

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800">Your Recommendations</h2>
        <p className="text-gray-600">Personalized insights and exercise plan</p>
      </div>

      {/* Plan Overview */}
      <Card>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <div className="text-sm text-gray-500">Current Plan</div>
              <Badge variant="active">Active</Badge>
            </div>
            <div className="text-xl font-semibold text-gray-900 mt-1">{plan.name}</div>
            <p className="text-sm text-gray-600 mt-2">{plan.goal}</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Duration</div>
            <div className="text-lg font-medium text-gray-900">{plan.duration}</div>
          </div>
        </div>
      </Card>

      {/* Insights Section */}
      <div>
        <h3 className="text-base font-medium text-gray-900 mb-4">Key Insights</h3>
        <div className="space-y-4">
          {insights.map((insight) => (
            <Card key={insight.id} className="border-l-4 border-l-gray-900">
              <div className="flex items-start justify-between mb-3">
                <h4 className="font-medium text-gray-900">{insight.title}</h4>
                <Badge variant={insight.severity === 'moderate' ? 'warning' : insight.severity === 'low' ? 'info' : 'success'}>
                  {insight.severity}
                </Badge>
              </div>
              <p className="text-sm text-gray-600 mb-3">{insight.description}</p>
              <div className="bg-gray-50 border border-gray-200 p-3 rounded-md">
                <div className="text-xs font-medium text-gray-700 mb-1">💡 Recommendation</div>
                <div className="text-sm text-gray-900">{insight.recommendation}</div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Exercise Plan Section */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-3">💪 Your Exercise Plan</h3>
        
        {Object.entries(exercisesByCategory).map(([category, exercises]) => (
          <div key={category} className="mb-6">
            <div className="flex items-center space-x-2 mb-3">
              <span className="text-sm font-medium text-gray-700 uppercase tracking-wide">
                {category}
              </span>
              <div className="flex-1 h-px bg-gray-200" />
              <span className="text-xs text-gray-500">{exercises.length} exercises</span>
            </div>

            <div className="space-y-3">
              {exercises.map((exercise) => (
                <Card key={exercise.id}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h4 className="font-medium text-gray-800">{exercise.name}</h4>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                          exercise.difficulty === 'Easy' ? 'bg-green-100 text-green-700' :
                          exercise.difficulty === 'Moderate' ? 'bg-blue-100 text-blue-700' :
                          'bg-orange-100 text-orange-700'
                        }`}>
                          {exercise.difficulty}
                        </span>
                      </div>

                      <p className="text-sm text-gray-600 mb-3">{exercise.instructions}</p>

                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <div className="flex items-center space-x-1">
                          <span>📊</span>
                          <span>{exercise.sets} sets × {exercise.reps}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <span>📅</span>
                          <span>{exercise.frequency}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <span>🎯</span>
                          <span>{exercise.targetArea}</span>
                        </div>
                      </div>
                    </div>

                    <button className="ml-4 p-2 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors">
                      <span className="text-2xl">▶️</span>
                    </button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Notes */}
      <Card>
        <div className="flex items-start space-x-3">
          <div className="text-2xl">📝</div>
          <div>
            <div className="font-medium text-gray-800 mb-1">Notes from Your Physiotherapist</div>
            <p className="text-sm text-gray-600">{plan.notes}</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
