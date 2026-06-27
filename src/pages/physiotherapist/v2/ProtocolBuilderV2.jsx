import { useState, useEffect } from 'react';
import Card from '../../../components/common/Card';
import { Plus, Save, Send, Edit, Trash2, AlertCircle, CheckCircle, Loader } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

/**
 * Protocol Builder (v2) — New Architecture
 *
 * Allows physiotherapists to:
 * - Create custom analysis protocols
 * - Define which joints/angles to track
 * - Set baseline metrics and risk factors
 * - Configure report templates
 * - Submit for superadmin approval
 */
export default function ProtocolBuilderV2({ currentUser }) {

  // Form state
  const [formData, setFormData] = useState({
    protocol_name: '',
    description: '',
    sport_id: '',
    config: {
      joints_to_track: [],
      angles_to_measure: [],
      metrics_to_calculate: [],
      baseline_metrics: {},
      risk_factors: {},
      report_template: { sections: [] },
      required_views: ['front'],
      expected_duration_seconds: 30,
    },
  });

  const [protocols, setProtocols] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [activeTab, setActiveTab] = useState('basic');
  const [editingId, setEditingId] = useState(null);

  // New field inputs for arrays
  const [newJoint, setNewJoint] = useState('');
  const [newAngle, setNewAngle] = useState('');
  const [newMetric, setNewMetric] = useState('');

  useEffect(() => {
    loadProtocols();
  }, []);

  const getUserId = () => {
    // Get user ID from currentUser or localStorage
    if (currentUser?.id) return currentUser.id;
    if (currentUser?.uid) return currentUser.uid;
    return localStorage.getItem('token') || 'unknown';
  };

  const loadProtocols = async () => {
    try {
      setLoading(true);
      const userId = getUserId();
      const response = await fetch(`${API_BASE_URL}/api/v1/protocols/my-drafts`, {
        headers: {
          'Authorization': `Bearer ${userId}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProtocols(data.protocols || []);
      }
    } catch (err) {
      console.error('Error loading protocols:', err);
      setError('Failed to load your protocols');
    } finally {
      setLoading(false);
    }
  };

  const loadProtocol = async (id) => {
    try {
      const userId = getUserId();
      const response = await fetch(`${API_BASE_URL}/api/v1/protocols/${id}`, {
        headers: {
          'Authorization': `Bearer ${userId}`,
        },
      });

      if (response.ok) {
        const protocol = await response.json();
        setFormData({
          protocol_name: protocol.protocol_name,
          description: protocol.description,
          sport_id: protocol.sport_id,
          config: protocol.config,
        });
        setIsEditing(true);
      }
    } catch (err) {
      console.error('Error loading protocol:', err);
      setError('Failed to load protocol');
    }
  };

  const handleSave = async () => {
    if (!formData.protocol_name || !formData.description || !formData.sport_id) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setSaving(true);
      setError(null);
      const userId = getUserId();

      const method = editingId ? 'PUT' : 'POST';
      const url = editingId
        ? `${API_BASE_URL}/api/v1/protocols/${editingId}`
        : `${API_BASE_URL}/api/v1/protocols`;

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userId}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const result = await response.json();
        setSuccess(`Protocol "${result.protocol_name}" saved as draft`);
        setEditingId(result.protocol_id);
        setTimeout(() => setSuccess(null), 3000);
        await loadProtocols();
      } else {
        const err = await response.json();
        setError(err.detail || 'Failed to save protocol');
      }
    } catch (err) {
      console.error('Error saving protocol:', err);
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleSubmitForApproval = async () => {
    if (!protocolId) {
      setError('Please save the protocol first');
      return;
    }

    try {
      setSaving(true);
      setError(null);
      const token = localStorage.getItem('token');

      const response = await fetch(`${API_BASE_URL}/api/v1/protocols/${protocolId}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token || currentUser?.id}`,
        },
        body: JSON.stringify({}),
      });

      if (response.ok) {
        const result = await response.json();
        setSuccess(`Protocol submitted for approval! Status: ${result.status}`);
        await loadProtocols();
        setTimeout(() => navigate('/physiotherapist/protocols'), 2000);
      } else {
        const err = await response.json();
        setError(err.detail || 'Failed to submit protocol');
      }
    } catch (err) {
      console.error('Error submitting protocol:', err);
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const addJoint = () => {
    if (newJoint.trim()) {
      setFormData(prev => ({
        ...prev,
        config: {
          ...prev.config,
          joints_to_track: [...prev.config.joints_to_track, newJoint.trim()],
        },
      }));
      setNewJoint('');
    }
  };

  const addAngle = () => {
    if (newAngle.trim()) {
      setFormData(prev => ({
        ...prev,
        config: {
          ...prev.config,
          angles_to_measure: [...prev.config.angles_to_measure, newAngle.trim()],
        },
      }));
      setNewAngle('');
    }
  };

  const addMetric = () => {
    if (newMetric.trim()) {
      setFormData(prev => ({
        ...prev,
        config: {
          ...prev.config,
          metrics_to_calculate: [...prev.config.metrics_to_calculate, newMetric.trim()],
        },
      }));
      setNewMetric('');
    }
  };

  const removeJoint = (index) => {
    setFormData(prev => ({
      ...prev,
      config: {
        ...prev.config,
        joints_to_track: prev.config.joints_to_track.filter((_, i) => i !== index),
      },
    }));
  };

  const removeAngle = (index) => {
    setFormData(prev => ({
      ...prev,
      config: {
        ...prev.config,
        angles_to_measure: prev.config.angles_to_measure.filter((_, i) => i !== index),
      },
    }));
  };

  const removeMetric = (index) => {
    setFormData(prev => ({
      ...prev,
      config: {
        ...prev.config,
        metrics_to_calculate: prev.config.metrics_to_calculate.filter((_, i) => i !== index),
      },
    }));
  };

  const handleStartNew = () => {
    setFormData({
      protocol_name: '',
      description: '',
      sport_id: '',
      config: {
        joints_to_track: [],
        angles_to_measure: [],
        metrics_to_calculate: [],
        baseline_metrics: {},
        risk_factors: {},
        report_template: { sections: [] },
        required_views: ['front'],
        expected_duration_seconds: 30,
      },
    });
    setEditingId(null);
    setIsEditing(false);
    setActiveTab('basic');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Custom Test Protocols</h1>
          <p className="text-gray-600">
            {isEditing ? 'Edit your protocol' : 'Create a new analysis protocol'}
          </p>
        </div>
        <button
          onClick={handleStartNew}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          <span>New Protocol</span>
        </button>
      </div>

      {/* Alerts */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-red-800 font-semibold">Error</p>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start space-x-3">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-green-800 font-semibold">Success</p>
            <p className="text-green-700">{success}</p>
          </div>
        </div>
      )}

      {/* Main Form */}
      <Card className="p-6">
        {/* Tabs */}
        <div className="flex space-x-4 border-b mb-6">
          {['basic', 'analysis', 'baseline', 'report'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 border-b-2 font-semibold ${
                activeTab === tab
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Basic Info Tab */}
        {activeTab === 'basic' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Protocol Name *
              </label>
              <input
                type="text"
                value={formData.protocol_name}
                onChange={(e) => setFormData({ ...formData, protocol_name: e.target.value })}
                placeholder="e.g., Football ACL Baseline"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Description *
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe the purpose and goals of this protocol"
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Sport ID *
              </label>
              <input
                type="text"
                value={formData.sport_id}
                onChange={(e) => setFormData({ ...formData, sport_id: e.target.value })}
                placeholder="e.g., football, basketball, soccer"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Expected Duration (seconds)
              </label>
              <input
                type="number"
                value={formData.config.expected_duration_seconds}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    config: {
                      ...formData.config,
                      expected_duration_seconds: parseInt(e.target.value),
                    },
                  })
                }
                min="10"
                max="300"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        )}

        {/* Analysis Config Tab */}
        {activeTab === 'analysis' && (
          <div className="space-y-6">
            {/* Joints to Track */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Joints to Track
              </label>
              <div className="flex space-x-2 mb-3">
                <input
                  type="text"
                  value={newJoint}
                  onChange={(e) => setNewJoint(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addJoint()}
                  placeholder="e.g., left_knee"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                />
                <button
                  onClick={addJoint}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.config.joints_to_track.map((joint, index) => (
                  <div key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full flex items-center space-x-2">
                    <span>{joint}</span>
                    <button
                      onClick={() => removeJoint(index)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Angles to Measure */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Angles to Measure
              </label>
              <div className="flex space-x-2 mb-3">
                <input
                  type="text"
                  value={newAngle}
                  onChange={(e) => setNewAngle(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addAngle()}
                  placeholder="e.g., knee_flexion"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                />
                <button
                  onClick={addAngle}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.config.angles_to_measure.map((angle, index) => (
                  <div key={index} className="bg-green-100 text-green-800 px-3 py-1 rounded-full flex items-center space-x-2">
                    <span>{angle}</span>
                    <button
                      onClick={() => removeAngle(index)}
                      className="text-green-600 hover:text-green-800"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Metrics to Calculate */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Metrics to Calculate
              </label>
              <div className="flex space-x-2 mb-3">
                <input
                  type="text"
                  value={newMetric}
                  onChange={(e) => setNewMetric(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addMetric()}
                  placeholder="e.g., range_of_motion"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                />
                <button
                  onClick={addMetric}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.config.metrics_to_calculate.map((metric, index) => (
                  <div key={index} className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full flex items-center space-x-2">
                    <span>{metric}</span>
                    <button
                      onClick={() => removeMetric(index)}
                      className="text-purple-600 hover:text-purple-800"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Baseline Metrics Tab (placeholder) */}
        {activeTab === 'baseline' && (
          <div className="text-gray-600 italic">
            <p>Configure baseline metrics here (coming soon)</p>
          </div>
        )}

        {/* Report Template Tab (placeholder) */}
        {activeTab === 'report' && (
          <div className="text-gray-600 italic">
            <p>Configure report sections and layout here (coming soon)</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-4 mt-8 pt-6 border-t">
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
          >
            {saving ? <Loader className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
            <span>{saving ? 'Saving...' : 'Save Draft'}</span>
          </button>

          {protocolId && (
            <button
              onClick={handleSubmitForApproval}
              disabled={saving}
              className="flex items-center space-x-2 bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400"
            >
              {saving ? <Loader className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              <span>{saving ? 'Submitting...' : 'Submit for Approval'}</span>
            </button>
          )}
        </div>
      </Card>

      {/* Recent Protocols List */}
      {protocols.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Your Draft Protocols</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {protocols.map(protocol => (
              <Card key={protocol.protocol_id} className="p-4">
                <h3 className="font-semibold text-gray-900 mb-2">{protocol.protocol_name}</h3>
                <p className="text-sm text-gray-600 mb-3">{protocol.description}</p>
                <div className="text-xs text-gray-500 mb-4">
                  <p>Sport: {protocol.sport_id}</p>
                  <p>Status: <span className="font-semibold">{protocol.status}</span></p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => navigate(`/physiotherapist/protocols/v2/${protocol.protocol_id}`)}
                    className="flex-1 text-blue-600 hover:text-blue-800 text-sm font-semibold flex items-center justify-center space-x-1"
                  >
                    <Edit className="w-4 h-4" />
                    <span>Edit</span>
                  </button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
