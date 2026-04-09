import { useState } from 'react'
import Card from '../../components/common/Card'
import Badge from '../../components/common/Badge'
import { exerciseLibrary } from '../../data/mockPhysioData'

export default function CaseDetail({ athleteCase, assessment, onBack, onUpdate }) {
  const [diagnosis, setDiagnosis] = useState(assessment?.diagnosis || '')
  const [selectedExercises, setSelectedExercises] = useState(assessment?.assignedExercises || [])
  const [showExerciseSelector, setShowExerciseSelector] = useState(false)

  const handleSave = () => {
    onUpdate(athleteCase.id, {
      diagnosis,
      assignedExercises: selectedExercises
    })
    alert('Case updated successfully!')
  }

  const toggleExercise = (exerciseId) => {
    if (selectedExercises.includes(exerciseId)) {
      setSelectedExercises(selectedExercises.filter(id => id !== exerciseId))
    } else {
      setSelectedExercises([...selectedExercises, exerciseId])
    }
  }

  const getSelectedExerciseDetails = () => {
    return exerciseLibrary.filter(ex => selectedExercises.includes(ex.id))
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <button
        onClick={onBack}
        className="flex items-center space-x-2 text-gray-900 hover:text-gray-700 font-medium"
      >
        <span>←</span>
        <span>Back to Case List</span>
      </button>

      {/* Case Header */}
      <Card>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              {athleteCase.athlete.avatar}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{athleteCase.athlete.name}</h2>
              <p className="text-gray-500">{athleteCase.athlete.sport} - Age {athleteCase.athlete.age}</p>
              <div className="flex items-center space-x-3 mt-1">
                <span className="text-sm text-gray-500">Case ID: {athleteCase.id}</span>
                <Badge variant={
                  athleteCase.status === 'active' ? 'active' :
                  athleteCase.status === 'assessment' ? 'new' :
                  'default'
                }>
                  {athleteCase.status}
                </Badge>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Condition</div>
            <div className="text-lg font-semibold text-gray-900">{athleteCase.condition}</div>
            <div className="text-sm text-gray-500 mt-1">Assigned: {athleteCase.assignedDate}</div>
          </div>
        </div>
      </Card>

      {/* Assessment Videos */}
      <Card title="Assessment Videos">
        {assessment?.videos && assessment.videos.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {assessment.videos.map((video) => (
              <div key={video.id} className="border border-gray-200 rounded-lg overflow-hidden">
                {/* Video Placeholder */}
                <div className="bg-gray-800 h-48 flex items-center justify-center relative">
                  <div className="text-center text-white">
                    <div className="text-6xl mb-2">🎥</div>
                    <div className="text-sm">Video Placeholder</div>
                  </div>
                  <button className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 hover:bg-opacity-30 transition-all">
                    <div className="w-16 h-16 bg-white bg-opacity-80 rounded-full flex items-center justify-center text-3xl">
                      ▶️
                    </div>
                  </button>
                </div>
                <div className="p-3">
                  <div className="font-medium text-gray-900">{video.title}</div>
                  <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
                    <span>⏱️ {video.duration}</span>
                    <Badge variant={video.status === 'analyzed' ? 'success' : 'info'}>
                      {video.status}
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-400 mt-1">{video.uploadDate}</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">📹</div>
            <div>No assessment videos uploaded yet</div>
          </div>
        )}
      </Card>

      {/* Physical Readings */}
      {assessment?.readings && (
        <Card title="Physical Readings">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Mobility */}
            {assessment.readings.mobility && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3 flex items-center space-x-2">
                  <span>📏</span>
                  <span>Mobility</span>
                </h4>
                <div className="space-y-2">
                  {Object.entries(assessment.readings.mobility).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span className="text-sm text-gray-600">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                      <div className="text-right">
                        <span className="text-sm font-medium">
                          L: {value.left}° / R: {value.right}°
                        </span>
                        <Badge
                          variant={
                            value.status === 'normal' ? 'success' :
                            value.status === 'limited' ? 'warning' :
                            'info'
                          }
                          className="ml-2"
                        >
                          {value.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Strength */}
            {assessment.readings.strength && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3 flex items-center space-x-2">
                  <span>💪</span>
                  <span>Strength</span>
                </h4>
                <div className="space-y-2">
                  {Object.entries(assessment.readings.strength).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span className="text-sm text-gray-600">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                      <div className="text-right">
                        <span className="text-sm font-medium">
                          {value.left !== undefined 
                            ? `L: ${value.left} / R: ${value.right} ${value.unit}`
                            : `${value.rating} ${value.unit}`
                          }
                        </span>
                        <Badge
                          variant={
                            value.status === 'good' ? 'success' :
                            value.status === 'moderate' ? 'info' :
                            'warning'
                          }
                          className="ml-2"
                        >
                          {value.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Pain */}
            {assessment.readings.pain && (
              <div className="md:col-span-2">
                <h4 className="font-medium text-gray-900 mb-3 flex items-center space-x-2">
                  <span>⚠️</span>
                  <span>Pain Assessment</span>
                </h4>
                <div className="space-y-2">
                  {Object.entries(assessment.readings.pain).map(([key, value]) => (
                    <div key={key} className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-gray-900">
                          {key.replace(/([A-Z])/g, ' $1').trim()}
                        </span>
                        <Badge variant="warning">{value.level}/10</Badge>
                      </div>
                      <div className="text-sm text-gray-600">{value.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Diagnosis Input */}
      <Card title="Diagnosis & Assessment Notes">
        <textarea
          value={diagnosis}
          onChange={(e) => setDiagnosis(e.target.value)}
          placeholder="Enter your diagnosis, findings, and recommendations..."
          className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
        <div className="mt-2 text-xs text-gray-500">
          Last updated: {athleteCase.lastUpdate}
        </div>
      </Card>

      {/* Exercise Assignment */}
      <Card title="Assigned Exercises">
        <div className="mb-4">
          <button
            onClick={() => setShowExerciseSelector(!showExerciseSelector)}
            className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors text-sm font-medium"
          >
            {showExerciseSelector ? 'Hide Exercise Library' : '+ Add Exercises'}
          </button>
        </div>

        {/* Exercise Selector */}
        {showExerciseSelector && (
          <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-3">Exercise Library</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-64 overflow-y-auto">
              {exerciseLibrary.map((exercise) => (
                <label
                  key={exercise.id}
                  className="flex items-start space-x-3 p-3 bg-white rounded border border-gray-200 hover:border-gray-900 cursor-pointer transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={selectedExercises.includes(exercise.id)}
                    onChange={() => toggleExercise(exercise.id)}
                    className="mt-1 w-4 h-4 text-blue-600"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 text-sm">{exercise.name}</div>
                    <div className="text-xs text-gray-500">
                      {exercise.category} • {exercise.difficulty} • {exercise.targetAreas.join(', ')}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Selected Exercises */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3">
            Currently Assigned ({selectedExercises.length})
          </h4>
          {getSelectedExerciseDetails().length > 0 ? (
            <div className="space-y-2">
              {getSelectedExerciseDetails().map((exercise) => (
                <div key={exercise.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900">{exercise.name}</div>
                    <div className="text-xs text-gray-500">
                      {exercise.category} • {exercise.difficulty}
                    </div>
                  </div>
                  <button
                    onClick={() => toggleExercise(exercise.id)}
                    className="text-gray-900 hover:text-gray-600 text-sm font-medium"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6 text-gray-500">
              <div className="text-3xl mb-2">📝</div>
              <div className="text-sm">No exercises assigned yet</div>
            </div>
          )}
        </div>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end space-x-3">
        <button
          onClick={onBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
        >
          Cancel
        </button>
        <button
          onClick={handleSave}
          className="px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors font-medium"
        >
          Save Changes
        </button>
      </div>
    </div>
  )
}
