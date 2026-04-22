import { useState, useEffect } from 'react'
import { collection, addDoc, query, where, onSnapshot, orderBy, serverTimestamp } from 'firebase/firestore'
import { db } from '../../firebase/config'
import { useAuth } from '../../context/AuthContext'
import Card from '../../components/common/Card'
import Badge from '../../components/common/Badge'

export default function RequestManagement() {
  const { user, userProfile } = useAuth()
  const [activeTab, setActiveTab] = useState('submit') // 'submit' or 'my-requests'
  const [requestType, setRequestType] = useState('exercise') // 'exercise' or 'baseline'
  const [myRequests, setMyRequests] = useState([])
  const [loading, setLoading] = useState(false)
  const [submitSuccess, setSubmitSuccess] = useState(false)

  // Exercise form state
  const [exerciseForm, setExerciseForm] = useState({
    exerciseName: '',
    description: '',
    category: 'strength',
    difficultyLevel: 'intermediate',
    targetMuscles: '',
    targetJoints: '',
    injuryTypes: '',
    instructions: '',
    precautions: '',
    durationMinutes: 10,
    equipmentNeeded: '',
    reason: '',
    useCase: ''
  })

  // Baseline form state
  const [baselineForm, setBaselineForm] = useState({
    measurementName: '',
    measurementType: 'functional',
    unit: '',
    sportId: 1,
    sportName: 'Football',
    applicableConditions: '',
    normalRangeMin: '',
    normalRangeMax: '',
    normalRangeDescription: '',
    testingProtocol: '',
    equipmentNeeded: '',
    reason: '',
    researchReferences: ''
  })

  const handleExerciseSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setSubmitSuccess(false)
    try {
      await addDoc(collection(db, 'physio_requests'), {
        type: 'exercise',
        status: 'pending',
        requesterUid: user?.uid,
        requesterName: userProfile?.displayName || user?.displayName,
        requesterEmail: user?.email,
        exerciseName: exerciseForm.exerciseName,
        description: exerciseForm.description,
        category: exerciseForm.category,
        difficultyLevel: exerciseForm.difficultyLevel,
        targetMuscles: exerciseForm.targetMuscles.split(',').map(s => s.trim()).filter(Boolean),
        targetJoints: exerciseForm.targetJoints.split(',').map(s => s.trim()).filter(Boolean),
        injuryTypes: exerciseForm.injuryTypes.split(',').map(s => s.trim()).filter(Boolean),
        instructions: exerciseForm.instructions,
        precautions: exerciseForm.precautions,
        durationMinutes: parseInt(exerciseForm.durationMinutes),
        equipmentNeeded: exerciseForm.equipmentNeeded.split(',').map(s => s.trim()).filter(Boolean),
        reason: exerciseForm.reason,
        useCase: exerciseForm.useCase,
        createdAt: serverTimestamp(),
      })
      setSubmitSuccess(true)
      setExerciseForm({ exerciseName: '', description: '', category: 'strength', difficultyLevel: 'intermediate', targetMuscles: '', targetJoints: '', injuryTypes: '', instructions: '', precautions: '', durationMinutes: 10, equipmentNeeded: '', reason: '', useCase: '' })
      setTimeout(() => setSubmitSuccess(false), 3000)
    } catch (error) {
      console.error('Error submitting request:', error)
      alert('Failed to submit request')
    } finally {
      setLoading(false)
    }
  }

  const handleBaselineSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setSubmitSuccess(false)
    try {
      await addDoc(collection(db, 'physio_requests'), {
        type: 'baseline',
        status: 'pending',
        requesterUid: user?.uid,
        requesterName: userProfile?.displayName || user?.displayName,
        requesterEmail: user?.email,
        measurementName: baselineForm.measurementName,
        measurementType: baselineForm.measurementType,
        unit: baselineForm.unit,
        sportId: parseInt(baselineForm.sportId),
        sportName: baselineForm.sportName,
        applicableConditions: baselineForm.applicableConditions.split(',').map(s => s.trim()).filter(Boolean),
        normalRangeMin: parseFloat(baselineForm.normalRangeMin) || 0,
        normalRangeMax: parseFloat(baselineForm.normalRangeMax) || 0,
        normalRangeDescription: baselineForm.normalRangeDescription,
        testingProtocol: baselineForm.testingProtocol,
        equipmentNeeded: baselineForm.equipmentNeeded.split(',').map(s => s.trim()).filter(Boolean),
        reason: baselineForm.reason,
        researchReferences: baselineForm.researchReferences.split(',').map(s => s.trim()).filter(Boolean),
        createdAt: serverTimestamp(),
      })
      setSubmitSuccess(true)
      setBaselineForm({ measurementName: '', measurementType: 'functional', unit: '', sportId: 1, sportName: 'Football', applicableConditions: '', normalRangeMin: '', normalRangeMax: '', normalRangeDescription: '', testingProtocol: '', equipmentNeeded: '', reason: '', researchReferences: '' })
      setTimeout(() => setSubmitSuccess(false), 3000)
    } catch (error) {
      console.error('Error submitting request:', error)
      alert('Failed to submit request')
    } finally {
      setLoading(false)
    }
  }

  const fetchMyRequests = () => {
    if (!user) return
    const q = query(
      collection(db, 'physio_requests'),
      where('requesterUid', '==', user.uid),
      orderBy('createdAt', 'desc')
    )
    return onSnapshot(q, (snap) => {
      setMyRequests(snap.docs.map(d => ({ id: d.id, ...d.data() })))
    })
  }

  // Fetch requests when switching to my-requests tab
  const handleTabChange = (tab) => {
    setActiveTab(tab)
    if (tab === 'my-requests') {
      fetchMyRequests()
    }
  }

  const getStatusBadge = (status) => {
    const variants = {
      pending: 'info',
      approved: 'success',
      rejected: 'error'
    }
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Request Management</h2>
        <p className="text-gray-600">Submit requests for new exercises or baseline measurements</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => handleTabChange('submit')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'submit'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Submit Request
          </button>
          <button
            onClick={() => handleTabChange('my-requests')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'my-requests'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            My Requests
          </button>
        </nav>
      </div>

      {submitSuccess && (
        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded">
          ✓ Request submitted successfully! An admin will review it soon.
        </div>
      )}

      {/* Submit Request Tab */}
      {activeTab === 'submit' && (
        <Card>
          {/* Request Type Selector */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Request Type</label>
            <div className="flex space-x-4">
              <button
                onClick={() => setRequestType('exercise')}
                className={`px-4 py-2 rounded-md ${
                  requestType === 'exercise'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                New Exercise
              </button>
              <button
                onClick={() => setRequestType('baseline')}
                className={`px-4 py-2 rounded-md ${
                  requestType === 'baseline'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                New Baseline Measurement
              </button>
            </div>
          </div>

          {/* Exercise Request Form */}
          {requestType === 'exercise' && (
            <form onSubmit={handleExerciseSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Exercise Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={exerciseForm.exerciseName}
                    onChange={(e) => setExerciseForm({ ...exerciseForm, exerciseName: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category *
                  </label>
                  <select
                    required
                    value={exerciseForm.category}
                    onChange={(e) => setExerciseForm({ ...exerciseForm, category: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="strength">Strength</option>
                    <option value="flexibility">Flexibility</option>
                    <option value="mobility">Mobility</option>
                    <option value="balance">Balance</option>
                    <option value="cardio">Cardio</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Difficulty Level *
                  </label>
                  <select
                    required
                    value={exerciseForm.difficultyLevel}
                    onChange={(e) => setExerciseForm({ ...exerciseForm, difficultyLevel: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Duration (minutes)
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={exerciseForm.durationMinutes}
                    onChange={(e) => setExerciseForm({ ...exerciseForm, durationMinutes: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description *
                </label>
                <textarea
                  required
                  rows="3"
                  value={exerciseForm.description}
                  onChange={(e) => setExerciseForm({ ...exerciseForm, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="Brief description of the exercise"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Step-by-Step Instructions *
                </label>
                <textarea
                  required
                  rows="5"
                  value={exerciseForm.instructions}
                  onChange={(e) => setExerciseForm({ ...exerciseForm, instructions: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="1. Start position&#10;2. Movement&#10;3. Return to start..."
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Target Muscles (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={exerciseForm.targetMuscles}
                    onChange={(e) => setExerciseForm({ ...exerciseForm, targetMuscles: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="e.g., hamstrings, glutes, core"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Target Joints (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={exerciseForm.targetJoints}
                    onChange={(e) => setExerciseForm({ ...exerciseForm, targetJoints: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="e.g., hip, knee, ankle"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Equipment Needed (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={exerciseForm.equipmentNeeded}
                    onChange={(e) => setExerciseForm({ ...exerciseForm, equipmentNeeded: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="e.g., dumbbell, mat"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Applicable Injury Types (comma-separated)
                </label>
                <input
                  type="text"
                  value={exerciseForm.injuryTypes}
                  onChange={(e) => setExerciseForm({ ...exerciseForm, injuryTypes: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="e.g., ACL recovery, hamstring strain"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Precautions
                </label>
                <textarea
                  rows="2"
                  value={exerciseForm.precautions}
                  onChange={(e) => setExerciseForm({ ...exerciseForm, precautions: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="Any precautions or contraindications"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Reason for Request *
                </label>
                <textarea
                  required
                  rows="2"
                  value={exerciseForm.reason}
                  onChange={(e) => setExerciseForm({ ...exerciseForm, reason: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="Why is this exercise needed in the library?"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Use Case
                </label>
                <textarea
                  rows="2"
                  value={exerciseForm.useCase}
                  onChange={(e) => setExerciseForm({ ...exerciseForm, useCase: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="When would you use this exercise?"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setExerciseForm({
                    exerciseName: '',
                    description: '',
                    category: 'strength',
                    difficultyLevel: 'intermediate',
                    targetMuscles: '',
                    targetJoints: '',
                    injuryTypes: '',
                    instructions: '',
                    precautions: '',
                    durationMinutes: 10,
                    equipmentNeeded: '',
                    reason: '',
                    useCase: ''
                  })}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Clear Form
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300"
                >
                  {loading ? 'Submitting...' : 'Submit Request'}
                </button>
              </div>
            </form>
          )}

          {/* Baseline Request Form */}
          {requestType === 'baseline' && (
            <form onSubmit={handleBaselineSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Measurement Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={baselineForm.measurementName}
                    onChange={(e) => setBaselineForm({ ...baselineForm, measurementName: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="e.g., Single Leg Hop Distance"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Measurement Type *
                  </label>
                  <select
                    required
                    value={baselineForm.measurementType}
                    onChange={(e) => setBaselineForm({ ...baselineForm, measurementType: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="functional">Functional</option>
                    <option value="strength">Strength</option>
                    <option value="mobility">Mobility</option>
                    <option value="endurance">Endurance</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Unit of Measurement *
                  </label>
                  <input
                    type="text"
                    required
                    value={baselineForm.unit}
                    onChange={(e) => setBaselineForm({ ...baselineForm, unit: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="e.g., cm, kg, %"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sport ID *
                  </label>
                  <input
                    type="number"
                    required
                    value={baselineForm.sportId}
                    onChange={(e) => setBaselineForm({ ...baselineForm, sportId: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sport Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={baselineForm.sportName}
                    onChange={(e) => setBaselineForm({ ...baselineForm, sportName: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="e.g., Football"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Normal Range
                </label>
                <div className="grid grid-cols-3 gap-4">
                  <input
                    type="number"
                    step="any"
                    value={baselineForm.normalRangeMin}
                    onChange={(e) => setBaselineForm({ ...baselineForm, normalRangeMin: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="Min value"
                  />
                  <input
                    type="number"
                    step="any"
                    value={baselineForm.normalRangeMax}
                    onChange={(e) => setBaselineForm({ ...baselineForm, normalRangeMax: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="Max value"
                  />
                  <input
                    type="text"
                    value={baselineForm.normalRangeDescription}
                    onChange={(e) => setBaselineForm({ ...baselineForm, normalRangeDescription: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="Description"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Applicable Conditions (comma-separated)
                </label>
                <input
                  type="text"
                  value={baselineForm.applicableConditions}
                  onChange={(e) => setBaselineForm({ ...baselineForm, applicableConditions: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="e.g., ACL recovery, ankle sprain"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Testing Protocol *
                </label>
                <textarea
                  required
                  rows="4"
                  value={baselineForm.testingProtocol}
                  onChange={(e) => setBaselineForm({ ...baselineForm, testingProtocol: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="How to perform this measurement..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Equipment Needed (comma-separated)
                </label>
                <input
                  type="text"
                  value={baselineForm.equipmentNeeded}
                  onChange={(e) => setBaselineForm({ ...baselineForm, equipmentNeeded: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="e.g., measuring tape, stopwatch"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Reason for Request *
                </label>
                <textarea
                  required
                  rows="2"
                  value={baselineForm.reason}
                  onChange={(e) => setBaselineForm({ ...baselineForm, reason: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="Why is this baseline measurement needed?"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Research References (comma-separated)
                </label>
                <input
                  type="text"
                  value={baselineForm.researchReferences}
                  onChange={(e) => setBaselineForm({ ...baselineForm, researchReferences: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="Citations or research backing this measurement"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setBaselineForm({
                    measurementName: '',
                    measurementType: 'functional',
                    unit: '',
                    sportId: 1,
                    sportName: 'Football',
                    applicableConditions: '',
                    normalRangeMin: '',
                    normalRangeMax: '',
                    normalRangeDescription: '',
                    testingProtocol: '',
                    equipmentNeeded: '',
                    reason: '',
                    researchReferences: ''
                  })}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Clear Form
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300"
                >
                  {loading ? 'Submitting...' : 'Submit Request'}
                </button>
              </div>
            </form>
          )}
        </Card>
      )}

      {/* My Requests Tab */}
      {activeTab === 'my-requests' && (
        <div className="space-y-6">
          {myRequests.length > 0 ? (
            myRequests.map((req) => (
              <Card key={req.id}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-xs bg-gray-100 px-2 py-0.5 rounded-full text-gray-600">{req.type}</span>
                      <h4 className="font-medium text-gray-900">{req.exerciseName || req.measurementName || 'Untitled'}</h4>
                      {getStatusBadge(req.status)}
                    </div>
                    {req.description && <p className="text-sm text-gray-600 mb-1">{req.description}</p>}
                    <div className="text-xs text-gray-500">
                      {req.category && `Category: ${req.category} | `}
                      Submitted: {req.createdAt?.toDate ? req.createdAt.toDate().toLocaleDateString() : '—'}
                    </div>
                    {req.adminNote && (
                      <div className="mt-2 p-2 bg-gray-50 rounded text-sm">
                        <span className="font-medium">Admin Note:</span> {req.adminNote}
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <Card>
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">📝</div>
                <div>No requests submitted yet</div>
                <button
                  onClick={() => setActiveTab('submit')}
                  className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                >
                  Submit Your First Request
                </button>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
