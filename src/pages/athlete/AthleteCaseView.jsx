import { useState } from 'react'
import Card from '../../components/common/Card'
import { athleteCase, getExercisesByDay, getCurrentWeekProgress } from '../../data/mockAthleteCase'

export default function AthleteCaseView() {
  const [activeTab, setActiveTab] = useState('overview')
  const { athlete, baseline, insights, plan, progress } = athleteCase

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              {athlete.avatar}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-800">{athlete.name}</h2>
              <p className="text-gray-600">{athlete.sport} - {athlete.position}</p>
              <p className="text-sm text-gray-500">ID: {athlete.id} | Age: {athlete.age}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="inline-block px-4 py-2 bg-green-100 text-green-700 rounded-full text-sm font-medium">
              Active Case
            </div>
            <p className="text-sm text-gray-500 mt-2">Last updated: {athleteCase.lastUpdated}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="flex border-b border-gray-200">
          {['overview', 'baseline', 'insights', 'plan', 'progress'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 font-medium text-sm transition-colors ${
                activeTab === tab
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <div className="text-sm text-gray-600 mb-1">Overall Progress</div>
                  <div className="text-3xl font-bold text-gray-800">{progress.overallProgress}%</div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${progress.overallProgress}%` }} />
                  </div>
                </Card>
                <Card>
                  <div className="text-sm text-gray-600 mb-1">Current Pain Level</div>
                  <div className="text-3xl font-bold text-gray-800">{getCurrentWeekProgress().painLevel}/10</div>
                  <div className="text-sm text-green-600 mt-2">↓ From baseline: 2/10</div>
                </Card>
                <Card>
                  <div className="text-sm text-gray-600 mb-1">This Week Compliance</div>
                  <div className="text-3xl font-bold text-gray-800">{getCurrentWeekProgress().compliance}%</div>
                  <div className="text-sm text-gray-500 mt-2">Week {getCurrentWeekProgress().week}</div>
                </Card>
              </div>

              <Card title="Recent Insights">
                <div className="space-y-3">
                  {insights.slice(0, 3).map((insight) => (
                    <div key={insight.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                      <span className={`text-2xl ${
                        insight.severity === 'moderate' ? '⚠️' : 
                        insight.severity === 'low' ? 'ℹ️' : '✅'
                      }`}>{insight.severity === 'moderate' ? '⚠️' : insight.severity === 'low' ? 'ℹ️' : '✅'}</span>
                      <div className="flex-1">
                        <div className="font-medium text-gray-800">{insight.title}</div>
                        <div className="text-sm text-gray-600 mt-1">{insight.recommendation}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {/* Baseline Tab */}
          {activeTab === 'baseline' && (
            <div className="space-y-6">
              <Card title="Video Assessments">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {baseline.videos.map((video) => (
                    <div key={video.id} className="border border-gray-200 rounded-lg overflow-hidden">
                      <div className="bg-gray-200 h-40 flex items-center justify-center text-6xl">
                        🎥
                      </div>
                      <div className="p-3">
                        <div className="font-medium text-gray-800">{video.title}</div>
                        <div className="text-sm text-gray-500">{video.duration}</div>
                        <div className="text-xs text-gray-600 mt-2">{video.notes}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              <Card title="Physical Readings">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-800 mb-3">Mobility</h4>
                    {Object.entries(baseline.readings.mobility).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between py-2 border-b border-gray-100">
                        <span className="text-sm text-gray-600">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                        <span className="text-sm font-medium">
                          L: {value.left}° / R: {value.right}° 
                          <span className="ml-2 text-green-600">({value.status})</span>
                        </span>
                      </div>
                    ))}
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-800 mb-3">Strength</h4>
                    {Object.entries(baseline.readings.strength).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between py-2 border-b border-gray-100">
                        <span className="text-sm text-gray-600">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                        <span className="text-sm font-medium">
                          {value.left !== undefined ? `L: ${value.left} / R: ${value.right} ${value.unit}` : `${value.rating} ${value.unit}`}
                          <span className="ml-2 text-green-600">({value.status})</span>
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Insights Tab */}
          {activeTab === 'insights' && (
            <div className="space-y-4">
              {insights.map((insight) => (
                <Card key={insight.id}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          insight.severity === 'moderate' ? 'bg-orange-100 text-orange-700' :
                          insight.severity === 'low' ? 'bg-blue-100 text-blue-700' :
                          'bg-green-100 text-green-700'
                        }`}>
                          {insight.severity}
                        </span>
                        <span className="text-xs text-gray-500">{insight.category}</span>
                      </div>
                      <h3 className="font-medium text-gray-800 mb-2">{insight.title}</h3>
                      <p className="text-sm text-gray-600 mb-2">{insight.description}</p>
                      <div className="bg-blue-50 p-3 rounded-lg">
                        <div className="text-xs font-medium text-blue-800 mb-1">Recommendation</div>
                        <div className="text-sm text-blue-700">{insight.recommendation}</div>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* Plan Tab */}
          {activeTab === 'plan' && (
            <div className="space-y-6">
              <Card>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <div className="text-sm text-gray-600">Plan Name</div>
                    <div className="font-medium text-gray-800">{plan.name}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Duration</div>
                    <div className="font-medium text-gray-800">{plan.duration}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Created By</div>
                    <div className="font-medium text-gray-800">{plan.createdBy}</div>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm font-medium text-gray-700">Goal</div>
                  <div className="text-sm text-gray-600">{plan.goal}</div>
                </div>
              </Card>

              <Card title="Exercises">
                <div className="space-y-3">
                  {plan.exercises.map((exercise) => (
                    <div key={exercise.id} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                      <div className="text-3xl">💪</div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="font-medium text-gray-800">{exercise.name}</h4>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            exercise.difficulty === 'Easy' ? 'bg-green-100 text-green-700' :
                            exercise.difficulty === 'Moderate' ? 'bg-blue-100 text-blue-700' :
                            'bg-orange-100 text-orange-700'
                          }`}>
                            {exercise.difficulty}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 mb-2">{exercise.instructions}</div>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span>📊 {exercise.sets} sets × {exercise.reps}</span>
                          <span>📅 {exercise.frequency}</span>
                          <span>🎯 {exercise.targetArea}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {/* Progress Tab */}
          {activeTab === 'progress' && (
            <div className="space-y-6">
              <Card title="Weekly Progress">
                <div className="space-y-3">
                  {progress.weeklyMetrics.map((week) => (
                    <div key={week.week} className={`p-4 rounded-lg ${
                      week.completed ? 'bg-gray-50' : 'bg-blue-50 border border-blue-200'
                    }`}>
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          <span className="font-medium text-gray-800">Week {week.week}</span>
                          <span className="text-sm text-gray-500">{week.date}</span>
                          {!week.completed && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                              Current
                            </span>
                          )}
                        </div>
                        <span className={`font-medium ${
                          week.compliance >= 90 ? 'text-green-600' :
                          week.compliance >= 70 ? 'text-blue-600' :
                          'text-orange-600'
                        }`}>
                          {week.compliance}% compliance
                        </span>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Pain: </span>
                          <span className="font-medium">{week.painLevel}/10</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Energy: </span>
                          <span className="font-medium">{week.energyLevel}/10</span>
                        </div>
                        <div className="col-span-3 text-gray-600 italic">{week.notes}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              <Card title="Performance Improvements">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(progress.improvements).map(([key, value]) => (
                    <div key={key} className="p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg">
                      <div className="text-sm text-gray-600 mb-2">
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </div>
                      <div className="flex items-baseline space-x-2 mb-1">
                        <span className="text-2xl font-bold text-gray-800">{value.current}</span>
                        <span className="text-sm text-gray-500">/ {value.target} {value.unit}</span>
                      </div>
                      <div className="text-sm font-medium text-green-600">{value.improvement}</div>
                      <div className="text-xs text-gray-500 mt-1">Baseline: {value.baseline}</div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
