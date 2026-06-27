import React, { useState, useEffect } from 'react';
import { CheckCircle2, XCircle, Clock, ChevronDown, ChevronUp } from 'lucide-react';

export default function ApprovalDashboard({ currentUser }) {
  const [requests, setRequests] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [protocols, setProtocols] = useState({});
  const [loading, setLoading] = useState(true);
  const [deciding, setDeciding] = useState(null);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectForm, setShowRejectForm] = useState(null);
  const [message, setMessage] = useState({ type: '', text: '' });

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';
  const token = localStorage.getItem('token') || currentUser?.id;

  useEffect(() => {
    fetchPendingRequests();
  }, []);

  const fetchPendingRequests = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/v1/protocol-requests/pending`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch requests');
      const data = await response.json();
      setRequests(data.requests || []);

      // Fetch protocol details for each request
      for (const req of data.requests || []) {
        if (!protocols[req.protocol_id]) {
          fetchProtocol(req.protocol_id);
        }
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  const fetchProtocol = async (protocolId) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/protocols/${protocolId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProtocols((prev) => ({ ...prev, [protocolId]: data }));
      }
    } catch (error) {
      console.error(`Error fetching protocol ${protocolId}:`, error);
    }
  };

  const handleApprove = async (requestId) => {
    if (deciding === requestId) return;

    try {
      setDeciding(requestId);
      const response = await fetch(`${API_URL}/api/v1/protocol-requests/${requestId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reason: '' }),
      });

      if (!response.ok) throw new Error('Failed to approve request');

      setMessage({ type: 'success', text: 'Protocol approved and published!' });
      setRequests((prev) => prev.filter((r) => r.request_id !== requestId));
      setSelectedRequest(null);

      // Refresh in 2 seconds
      setTimeout(fetchPendingRequests, 2000);
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` });
    } finally {
      setDeciding(null);
    }
  };

  const handleReject = async (requestId, reason) => {
    if (!reason.trim()) {
      setMessage({ type: 'error', text: 'Please provide a rejection reason' });
      return;
    }

    if (deciding === requestId) return;

    try {
      setDeciding(requestId);
      const response = await fetch(`${API_URL}/api/v1/protocol-requests/${requestId}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reason }),
      });

      if (!response.ok) throw new Error('Failed to reject request');

      setMessage({ type: 'success', text: 'Protocol rejected. Physiotherapist notified.' });
      setRequests((prev) => prev.filter((r) => r.request_id !== requestId));
      setSelectedRequest(null);
      setRejectReason('');
      setShowRejectForm(null);

      // Refresh in 2 seconds
      setTimeout(fetchPendingRequests, 2000);
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` });
    } finally {
      setDeciding(null);
    }
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString();
  };

  if (!currentUser) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
          <p className="text-gray-600">Please log in with a superadmin account</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-6 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Protocol Approval Dashboard</h1>
          <p className="mt-2 text-gray-600">Review and approve physiotherapist-created protocols</p>
        </div>

        {message.text && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.type === 'success' 
              ? 'bg-green-50 border border-green-200 text-green-800' 
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}>
            {message.text}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading pending requests...</p>
          </div>
        ) : requests.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">All Caught Up!</h2>
            <p className="text-gray-600">No pending protocol requests to review</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Request List */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                  <h2 className="text-lg font-semibold text-gray-900">
                    Pending Requests ({requests.length})
                  </h2>
                </div>
                <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                  {requests.map((request) => (
                    <button
                      key={request.request_id}
                      onClick={() => setSelectedRequest(request)}
                      className={`w-full px-6 py-4 text-left hover:bg-gray-50 transition ${
                        selectedRequest?.request_id === request.request_id
                          ? 'bg-blue-50 border-l-4 border-blue-600'
                          : ''
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">
                            {protocols[request.protocol_id]?.protocol_name || 'Loading...'}
                          </div>
                          <div className="text-sm text-gray-600 mt-1">
                            by {request.requested_by}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {formatDate(request.created_at)}
                          </div>
                        </div>
                        <Clock className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-1" />
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Request Details & Actions */}
            <div className="lg:col-span-2">
              {selectedRequest ? (
                <div className="bg-white rounded-lg shadow">
                  <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <h2 className="text-lg font-semibold text-gray-900">Request Details</h2>
                  </div>

                  <div className="p-6 space-y-6">
                    {/* Protocol Info */}
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">Protocol Information</h3>
                      {protocols[selectedRequest.protocol_id] ? (
                        <div className="space-y-3 bg-gray-50 p-4 rounded-lg">
                          <div>
                            <div className="text-sm font-medium text-gray-600">Name</div>
                            <div className="text-gray-900">
                              {protocols[selectedRequest.protocol_id].protocol_name}
                            </div>
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-600">Sport</div>
                            <div className="text-gray-900">
                              {protocols[selectedRequest.protocol_id].sport_id}
                            </div>
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-600">Description</div>
                            <div className="text-gray-900">
                              {protocols[selectedRequest.protocol_id].description}
                            </div>
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-600">Created By</div>
                            <div className="text-gray-900">
                              {protocols[selectedRequest.protocol_id].created_by}
                            </div>
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-600">Submitted</div>
                            <div className="text-gray-900">
                              {formatDate(selectedRequest.created_at)}
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="text-gray-600">Loading protocol details...</div>
                      )}
                    </div>

                    {/* Analysis Config */}
                    {protocols[selectedRequest.protocol_id]?.config && (
                      <div>
                        <h3 className="font-semibold text-gray-900 mb-3">Analysis Configuration</h3>
                        <div className="space-y-3 bg-gray-50 p-4 rounded-lg text-sm">
                          <div>
                            <div className="font-medium text-gray-600">Joints to Track</div>
                            <div className="text-gray-900">
                              {protocols[selectedRequest.protocol_id].config.joints_to_track?.join(', ') || 'None'}
                            </div>
                          </div>
                          <div>
                            <div className="font-medium text-gray-600">Angles to Measure</div>
                            <div className="text-gray-900">
                              {protocols[selectedRequest.protocol_id].config.angles_to_measure?.join(', ') || 'None'}
                            </div>
                          </div>
                          <div>
                            <div className="font-medium text-gray-600">Metrics to Calculate</div>
                            <div className="text-gray-900">
                              {protocols[selectedRequest.protocol_id].config.metrics_to_calculate?.join(', ') || 'None'}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Decision Section */}
                    <div className="border-t border-gray-200 pt-6">
                      <h3 className="font-semibold text-gray-900 mb-4">Your Decision</h3>

                      {/* Approve Button */}
                      <button
                        onClick={() => handleApprove(selectedRequest.request_id)}
                        disabled={deciding === selectedRequest.request_id}
                        className="w-full mb-3 px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition flex items-center justify-center"
                      >
                        <CheckCircle2 className="w-5 h-5 mr-2" />
                        {deciding === selectedRequest.request_id ? 'Approving...' : 'Approve Protocol'}
                      </button>

                      {/* Reject Section */}
                      {showRejectForm === selectedRequest.request_id ? (
                        <div className="space-y-3">
                          <textarea
                            value={rejectReason}
                            onChange={(e) => setRejectReason(e.target.value)}
                            placeholder="Please provide a reason for rejection..."
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                            rows={3}
                          />
                          <div className="flex gap-3">
                            <button
                              onClick={() => handleReject(selectedRequest.request_id, rejectReason)}
                              disabled={deciding === selectedRequest.request_id}
                              className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition flex items-center justify-center"
                            >
                              <XCircle className="w-4 h-4 mr-2" />
                              {deciding === selectedRequest.request_id ? 'Rejecting...' : 'Confirm Reject'}
                            </button>
                            <button
                              onClick={() => {
                                setShowRejectForm(null);
                                setRejectReason('');
                              }}
                              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button
                          onClick={() => setShowRejectForm(selectedRequest.request_id)}
                          className="w-full px-4 py-3 border-2 border-red-600 hover:bg-red-50 text-red-600 rounded-lg font-medium transition flex items-center justify-center"
                        >
                          <XCircle className="w-5 h-5 mr-2" />
                          Reject Protocol
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-lg shadow p-8 text-center text-gray-600">
                  Select a protocol request to review
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
