import { useState, useEffect } from 'react'
import Card from '../../components/common/Card'
import Badge from '../../components/common/Badge'
import { Plus, Edit, Trash2, Play, FileText, Video, Settings } from 'lucide-react'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080'

export default function ProtocolBuilder({ currentUser }) {
  const [protocols, setProtocols] = useState([])
  const [showBuilder, setShowBuilder] = useState(false)
  const [editingProtocol, setEditingProtocol] = useState(null)
  const [loading, setLoading] = useState(false)

  // Form state
  const [formData, setFormData] = useState({
    protocol_name: '',
    description: '',
    sport_id: '',
    test_category: 'baseline',
    video_instructions: {
      setup: '',
      athlete_actions: [],
      camera_positions: []
    },
    required_views: ['front'],
    duration_seconds: 30,
    equipment_needed: [],
    analysis_config: {
      joints_to_track: [],
      metrics_to_calculate: [],
      angles_to_measure: []
    },
    baseline_metrics: {},
    risk_factors: {},
    report_template: {
      sections: [],
      summary_fields: []
    }
  })

  useEffect(() => {
    loadProtocols()
  }, [])

  const loadProtocols = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_BASE_URL}/api/protocols`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setProtocols(data.protocols)
      }
    } catch (error) {
      console.error('Error loading protocols:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const token = localStorage.getItem('token')
      const url = editingProtocol
        ? `${API_BASE_URL}/api/protocols/${editingProtocol.protocol_id}`
        : `${API_BASE_URL}/api/protocols`

      const method = editingProtocol ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        await loadProtocols()
        setShowBuilder(false)
        setEditingProtocol(null)
        resetForm()
      } else {
        const error = await response.json()
        alert(error.error || 'Failed to save protocol')
      }
    } catch (error) {
      console.error('Error saving protocol:', error)
      alert('Failed to save protocol')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setFormData({
      protocol_name: '',
      description: '',
      sport_id: '',
      test_category: 'baseline',
      video_instructions: {
        setup: '',
        athlete_actions: [],
        camera_positions: []
      },
      required_views: ['front'],
      duration_seconds: 30,
      equipment_needed: [],
      analysis_config: {
        joints_to_track: [],
        metrics_to_calculate: [],
        angles_to_measure: []
      },
      baseline_metrics: {},
      risk_factors: {},
      report_template: {
        sections: [],
        summary_fields: []
      }
    })
  }

  const startEdit = (protocol) => {
    setEditingProtocol(protocol)
    setFormData({
      protocol_name: protocol.protocol_name,
      description: protocol.description,
      sport_id: protocol.sport_id,
      test_category: protocol.test_category,
      video_instructions: protocol.video_instructions || formData.video_instructions,
      required_views: protocol.required_views || formData.required_views,
      duration_seconds: protocol.duration_seconds || formData.duration_seconds,
      equipment_needed: protocol.equipment_needed || formData.equipment_needed,
      analysis_config: protocol.analysis_config || formData.analysis_config,
      baseline_metrics: protocol.baseline_metrics || formData.baseline_metrics,
      risk_factors: protocol.risk_factors || formData.risk_factors,
      report_template: protocol.report_template || formData.report_template
    })
    setShowBuilder(true)
  }

  const addArrayItem = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: [...prev[field], value]
    }))
  }

  const removeArrayItem = (field, index) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }))
  }

  const updateNestedField = (path, value) => {
    setFormData(prev => {
      const keys = path.split('.')
      const lastKey = keys.pop()
      const target = keys.reduce((obj, key) => obj[key], prev)
      target[lastKey] = value
      return { ...prev }
    })
  }

  const executeProtocol = async (protocolId) => {
    const athleteId = prompt('Enter athlete ID to execute protocol:')
    if (!athleteId) return

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_BASE_URL}/api/protocols/${protocolId}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ athlete_id: athleteId })
      })

      if (response.ok) {
        const data = await response.json()
        alert(`Protocol execution started! Execution ID: ${data.execution.execution_id}`)
      } else {
        const error = await response.json()
        alert(error.error || 'Failed to execute protocol')
      }
    } catch (error) {
      console.error('Error executing protocol:', error)
      alert('Failed to execute protocol')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Custom Test Protocols</h1>
          <p className="text-gray-600">Define custom baseline tests and analysis procedures</p>
        </div>
        <button
          onClick={() => setShowBuilder(true)}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          <span>Create Protocol</span>
        </button>
      </div>

      {/* Protocol List */}
      {!showBuilder && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {protocols.map(protocol => (
            <Card key={protocol.protocol_id} className="relative">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{protocol.protocol_name}</h3>
                  <p className="text-sm text-gray-600">{protocol.description}</p>
                </div>
                <Badge variant="info">{protocol.test_category}</Badge>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Video className="w-4 h-4" />
                  <span>{protocol.required_views?.join(', ') || 'front'}</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Settings className="w-4 h-4" />
                  <span>{protocol.sport_id}</span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex space-x-2">
                  <button
                    onClick={() => startEdit(protocol)}
                    className="p-2 text-gray-600 hover:text-blue-600"
                    title="Edit"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => executeProtocol(protocol.protocol_id)}
                    className="p-2 text-gray-600 hover:text-green-600"
                    title="Execute"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                </div>
                <div className="text-xs text-gray-500">
                  {new Date(protocol.created_at).toLocaleDateString()}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Protocol Builder */}
      {showBuilder && (
        <Card title={editingProtocol ? 'Edit Protocol' : 'Create New Protocol'}>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Protocol Name *
                </label>
                <input
                  type="text"
                  value={formData.protocol_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, protocol_name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sport ID *
                </label>
                <input
                  type="text"
                  value={formData.sport_id}
                  onChange={(e) => setFormData(prev => ({ ...prev, sport_id: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., soccer, basketball"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                rows={3}
              />
            </div>

            {/* Video Instructions */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Video Recording Instructions</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Setup Instructions
                  </label>
                  <textarea
                    value={formData.video_instructions.setup}
                    onChange={(e) => updateNestedField('video_instructions.setup', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="How to set up the camera and environment..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Athlete Actions
                  </label>
                  <div className="space-y-2">
                    {formData.video_instructions.athlete_actions.map((action, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <input
                          type="text"
                          value={action}
                          onChange={(e) => {
                            const newActions = [...formData.video_instructions.athlete_actions]
                            newActions[index] = e.target.value
                            updateNestedField('video_instructions.athlete_actions', newActions)
                          }}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          placeholder="What should the athlete do..."
                        />
                        <button
                          type="button"
                          onClick={() => {
                            const newActions = formData.video_instructions.athlete_actions.filter((_, i) => i !== index)
                            updateNestedField('video_instructions.athlete_actions', newActions)
                          }}
                          className="p-2 text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                    <button
                      type="button"
                      onClick={() => addArrayItem('video_instructions.athlete_actions', '')}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      + Add Action
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Analysis Configuration */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Analysis Configuration</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Joints to Track
                  </label>
                  <input
                    type="text"
                    value={formData.analysis_config.joints_to_track.join(', ')}
                    onChange={(e) => updateNestedField('analysis_config.joints_to_track', e.target.value.split(',').map(s => s.trim()))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., left_knee, right_hip, left_shoulder"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Angles to Measure
                  </label>
                  <input
                    type="text"
                    value={formData.analysis_config.angles_to_measure.join(', ')}
                    onChange={(e) => updateNestedField('analysis_config.angles_to_measure', e.target.value.split(',').map(s => s.trim()))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., knee_flexion, hip_angle, shoulder_elevation"
                  />
                </div>
              </div>
            </div>

            {/* Form Actions */}
            <div className="flex items-center justify-end space-x-4 pt-6 border-t">
              <button
                type="button"
                onClick={() => {
                  setShowBuilder(false)
                  setEditingProtocol(null)
                  resetForm()
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Saving...' : (editingProtocol ? 'Update Protocol' : 'Create Protocol')}
              </button>
            </div>
          </form>
        </Card>
      )}
    </div>
  )
}