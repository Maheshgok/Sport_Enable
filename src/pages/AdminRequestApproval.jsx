import { useState, useEffect } from 'react'
import Card from '../components/common/Card'
import Badge from '../components/common/Badge'

export default function AdminRequestApproval() {
  const [requests, setRequests] = useState({ exerciseRequests: [], baselineRequests: [] })
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('pending') // 'all', 'pending', 'approved', 'rejected'
  const [selectedRequest, setSelectedRequest] = useState(null)
  const [reviewNotes, setReviewNotes] = useState('')
  const [showReviewModal, setShowReviewModal] = useState(false)
  const [reviewAction, setReviewAction] = useState(null) // 'approve' or 'reject'

  useEffect(() => {
    fetchRequests()
  }, [filter])

  const fetchRequests = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('token')
      const statusParam = filter === 'all' ? 'all' : filter
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/admin/requests?status=${statusParam}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      if (response.ok) {
        const data = await response.json()
        setRequests(data)
      }
    } catch (error) {
      console.error('Error fetching requests:', error)
    } finally {
      setLoading(false)
    }
  }

  const openReviewModal = (request, requestType, action) => {
    setSelectedRequest({ ...request, requestType })
    setReviewAction(action)
    setReviewNotes('')
    setShowReviewModal(true)
  }

  const handleReview = async () => {
    if (!selectedRequest) return

    try {
      const token = localStorage.getItem('token')
      let endpoint = ''
      let body = { reviewNotes }

      if (reviewAction === 'approve') {
        if (selectedRequest.requestType === 'exercise') {
          endpoint = `/api/admin/requests/exercise/${selectedRequest.requestId}/approve`
          body.addToLibrary = true
        } else {
          endpoint = `/api/admin/requests/baseline/${selectedRequest.requestId}/approve`
        }
      } else {
        endpoint = `/api/admin/requests/${selectedRequest.requestId}/reject`
        body.requestType = selectedRequest.requestType
      }

      const response = await fetch(`${import.meta.env.VITE_API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(body)
      })

      if (response.ok) {
        setShowReviewModal(false)
        fetchRequests() // Refresh the list
        alert(`Request ${reviewAction}d successfully!`)
      } else {
        const error = await response.json()
        alert(`Error: ${error.error}`)
      }
    } catch (error) {
      console.error('Error reviewing request:', error)
      alert('Failed to review request')
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

  const totalPending = requests.exerciseRequests.filter(r => r.status === 'pending').length +
    requests.baselineRequests.filter(r => r.status === 'pending').length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Request Approval</h2>
          <p className="text-gray-600">Review and approve exercise and baseline requests from physiotherapists</p>
        </div>
        {totalPending > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 px-4 py-2 rounded-lg">
            <span className="text-yellow-800 font-medium">{totalPending} Pending Review</span>
          </div>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {['pending', 'approved', 'rejected', 'all'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`py-2 px-1 border-b-2 font-medium text-sm capitalize ${
                filter === status
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {status}
            </button>
          ))}
        </nav>
      </div>

      {loading ? (
        <Card>
          <div className="text-center py-8 text-gray-500">Loading requests...</div>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* Exercise Requests */}
          {requests.exerciseRequests.length > 0 && (
            <Card title={`Exercise Requests (${requests.exerciseRequests.length})`}>
              <div className="space-y-4">
                {requests.exerciseRequests.map((req) => (
                  <div key={req.requestId} className="p-4 border border-gray-200 rounded-lg hover:border-gray-300">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-1">
                          <h3 className="text-lg font-semibold text-gray-900">{req.exerciseName}</h3>
                          {getStatusBadge(req.status)}
                        </div>
                        <div className="text-sm text-gray-500">
                          Requested by {req.requestedByName} ({req.requestedByEmail})
                        </div>
                        <div className="text-xs text-gray-400">
                          {new Date(req.createdAt?.seconds * 1000 || Date.now()).toLocaleDateString()}
                        </div>
                      </div>
                      {req.status === 'pending' && (
                        <div className="flex space-x-2">
                          <button
                            onClick={() => openReviewModal(req, 'exercise', 'approve')}
                            className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600"
                          >
                            ✓ Approve
                          </button>
                          <button
                            onClick={() => openReviewModal(req, 'exercise', 'reject')}
                            className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600"
                          >
                            ✗ Reject
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Details */}
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-700">Category:</span> {req.category}
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Difficulty:</span> {req.difficultyLevel}
                      </div>
                      <div className="col-span-2">
                        <span className="font-medium text-gray-700">Description:</span> {req.description}
                      </div>
                      <div className="col-span-2">
                        <span className="font-medium text-gray-700">Instructions:</span>
                        <div className="mt-1 p-2 bg-gray-50 rounded text-xs whitespace-pre-line">
                          {req.instructions}
                        </div>
                      </div>
                      {req.targetMuscles && req.targetMuscles.length > 0 && (
                        <div className="col-span-2">
                          <span className="font-medium text-gray-700">Target Muscles:</span> {req.targetMuscles.join(', ')}
                        </div>
                      )}
                      {req.injuryTypes && req.injuryTypes.length > 0 && (
                        <div className="col-span-2">
                          <span className="font-medium text-gray-700">Applicable Injuries:</span> {req.injuryTypes.join(', ')}
                        </div>
                      )}
                      <div className="col-span-2">
                        <span className="font-medium text-gray-700">Justification:</span>
                        <div className="mt-1 p-2 bg-blue-50 rounded text-xs">
                          {req.reason}
                        </div>
                      </div>
                      {req.reviewNotes && (
                        <div className="col-span-2">
                          <span className="font-medium text-gray-700">Review Notes:</span>
                          <div className="mt-1 p-2 bg-gray-50 rounded text-xs">
                            {req.reviewNotes}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Baseline Requests */}
          {requests.baselineRequests.length > 0 && (
            <Card title={`Baseline Measurement Requests (${requests.baselineRequests.length})`}>
              <div className="space-y-4">
                {requests.baselineRequests.map((req) => (
                  <div key={req.requestId} className="p-4 border border-gray-200 rounded-lg hover:border-gray-300">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-1">
                          <h3 className="text-lg font-semibold text-gray-900">{req.measurementName}</h3>
                          {getStatusBadge(req.status)}
                        </div>
                        <div className="text-sm text-gray-500">
                          Requested by {req.requestedByName} ({req.requestedByEmail})
                        </div>
                        <div className="text-xs text-gray-400">
                          {new Date(req.createdAt?.seconds * 1000 || Date.now()).toLocaleDateString()}
                        </div>
                      </div>
                      {req.status === 'pending' && (
                        <div className="flex space-x-2">
                          <button
                            onClick={() => openReviewModal(req, 'baseline', 'approve')}
                            className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600"
                          >
                            ✓ Approve
                          </button>
                          <button
                            onClick={() => openReviewModal(req, 'baseline', 'reject')}
                            className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600"
                          >
                            ✗ Reject
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Details */}
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-700">Type:</span> {req.measurementType}
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Unit:</span> {req.unit}
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Sport:</span> {req.sportName}
                      </div>
                      {req.normalRange && (
                        <div>
                          <span className="font-medium text-gray-700">Normal Range:</span> {req.normalRange.min} - {req.normalRange.max}
                        </div>
                      )}
                      {req.applicableConditions && req.applicableConditions.length > 0 && (
                        <div className="col-span-2">
                          <span className="font-medium text-gray-700">Applicable Conditions:</span> {req.applicableConditions.join(', ')}
                        </div>
                      )}
                      <div className="col-span-2">
                        <span className="font-medium text-gray-700">Testing Protocol:</span>
                        <div className="mt-1 p-2 bg-gray-50 rounded text-xs whitespace-pre-line">
                          {req.testingProtocol}
                        </div>
                      </div>
                      <div className="col-span-2">
                        <span className="font-medium text-gray-700">Justification:</span>
                        <div className="mt-1 p-2 bg-blue-50 rounded text-xs">
                          {req.reason}
                        </div>
                      </div>
                      {req.reviewNotes && (
                        <div className="col-span-2">
                          <span className="font-medium text-gray-700">Review Notes:</span>
                          <div className="mt-1 p-2 bg-gray-50 rounded text-xs">
                            {req.reviewNotes}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {requests.exerciseRequests.length === 0 && requests.baselineRequests.length === 0 && (
            <Card>
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">✅</div>
                <div>No {filter === 'all' ? '' : filter} requests</div>
              </div>
            </Card>
          )}
        </div>
      )}

      {/* Review Modal */}
      {showReviewModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">
              {reviewAction === 'approve' ? 'Approve' : 'Reject'} Request
            </h3>
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                <span className="font-medium">Request:</span> {selectedRequest?.exerciseName || selectedRequest?.measurementName}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Requested by:</span> {selectedRequest?.requestedByName}
              </p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Review Notes {reviewAction === 'reject' && <span className="text-red-500">*</span>}
              </label>
              <textarea
                rows="4"
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder={reviewAction === 'approve' 
                  ? 'Optional notes for the requester...' 
                  : 'Please explain why this request is being rejected...'}
              />
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowReviewModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleReview}
                disabled={reviewAction === 'reject' && !reviewNotes}
                className={`px-4 py-2 rounded-md text-white ${
                  reviewAction === 'approve'
                    ? 'bg-green-500 hover:bg-green-600'
                    : 'bg-red-500 hover:bg-red-600'
                } disabled:bg-gray-300 disabled:cursor-not-allowed`}
              >
                {reviewAction === 'approve' ? 'Approve' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
