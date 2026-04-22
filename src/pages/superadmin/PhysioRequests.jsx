import { useState, useEffect } from 'react'
import { collection, query, onSnapshot, doc, updateDoc, orderBy, addDoc, serverTimestamp } from 'firebase/firestore'
import { db } from '../../firebase/config'
import { useAuth } from '../../context/AuthContext'

const TYPE_LABEL = { exercise: 'Exercise', baseline: 'Baseline Measurement', analysis: 'Analysis Type' }
const STATUS_COLOR = {
  pending: 'bg-amber-100 text-amber-700',
  approved: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  'in-review': 'bg-blue-100 text-blue-700',
}

export default function PhysioRequests() {
  const [requests, setRequests] = useState([])
  const [filter, setFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const [expanded, setExpanded] = useState(null)
  const [note, setNote] = useState('')
  const [saving, setSaving] = useState(null)

  useEffect(() => {
    const q = query(collection(db, 'physio_requests'), orderBy('createdAt', 'desc'))
    return onSnapshot(q, (snap) => {
      setRequests(snap.docs.map(d => ({ id: d.id, ...d.data() })))
    })
  }, [])

  const updateStatus = async (id, status) => {
    setSaving(id)
    try {
      await updateDoc(doc(db, 'physio_requests', id), {
        status,
        adminNote: note,
        reviewedAt: serverTimestamp(),
      })
      setExpanded(null)
      setNote('')
    } catch (e) { console.error(e) }
    setSaving(null)
  }

  const filtered = requests.filter(r => {
    const matchStatus = filter === 'all' || r.status === filter
    const matchType = typeFilter === 'all' || r.type === typeFilter
    return matchStatus && matchType
  })

  const stats = {
    total: requests.length,
    pending: requests.filter(r => r.status === 'pending').length,
    approved: requests.filter(r => r.status === 'approved').length,
    rejected: requests.filter(r => r.status === 'rejected').length,
  }

  const statusBadge = (status) => (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLOR[status] || 'bg-gray-100 text-gray-600'}`}>{status}</span>
  )

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">Physiotherapist Requests</h2>
        <p className="text-sm text-gray-500 mt-1">Review requests for new exercises, baseline measurements, and analysis types.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {[
          { label: 'Total', value: stats.total, color: 'border-gray-200' },
          { label: 'Pending', value: stats.pending, color: 'border-amber-200', textColor: 'text-amber-700' },
          { label: 'Approved', value: stats.approved, color: 'border-green-200', textColor: 'text-green-700' },
          { label: 'Rejected', value: stats.rejected, color: 'border-red-200', textColor: 'text-red-700' },
        ].map(s => (
          <div key={s.label} className={`bg-white rounded-xl border ${s.color} p-4`}>
            <div className={`text-2xl font-bold ${s.textColor || 'text-gray-900'}`}>{s.value}</div>
            <div className="text-xs text-gray-500">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-4 flex-wrap">
        <select value={filter} onChange={e => setFilter(e.target.value)} className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
          <option value="all">All statuses</option>
          <option value="pending">Pending</option>
          <option value="in-review">In Review</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
        <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)} className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
          <option value="all">All types</option>
          <option value="exercise">Exercise</option>
          <option value="baseline">Baseline Measurement</option>
          <option value="analysis">Analysis Type</option>
        </select>
      </div>

      {/* Requests list */}
      {filtered.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center text-gray-400 text-sm">No requests found</div>
      ) : (
        <div className="space-y-3">
          {filtered.map(r => (
            <div key={r.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div className="flex items-start justify-between p-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">{TYPE_LABEL[r.type] || r.type}</span>
                    {statusBadge(r.status)}
                  </div>
                  <div className="font-medium text-gray-900">{r.title || r.exerciseName || r.measurementName || 'Untitled'}</div>
                  <div className="text-xs text-gray-500 mt-0.5">
                    by {r.requesterName || r.requesterEmail} · {r.createdAt?.toDate ? r.createdAt.toDate().toLocaleDateString('en-GB') : '—'}
                  </div>
                </div>
                <button
                  onClick={() => setExpanded(expanded === r.id ? null : r.id)}
                  className="ml-3 text-xs text-gray-500 hover:text-gray-900 underline whitespace-nowrap"
                >
                  {expanded === r.id ? 'Collapse' : 'Review'}
                </button>
              </div>

              {expanded === r.id && (
                <div className="border-t border-gray-100 p-4 bg-gray-50 space-y-4">
                  {/* Details */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    {r.description && <div><span className="text-xs font-semibold text-gray-500 block">Description</span>{r.description}</div>}
                    {r.category && <div><span className="text-xs font-semibold text-gray-500 block">Category</span>{r.category}</div>}
                    {r.reason && <div><span className="text-xs font-semibold text-gray-500 block">Reason</span>{r.reason}</div>}
                    {r.useCase && <div><span className="text-xs font-semibold text-gray-500 block">Use Case</span>{r.useCase}</div>}
                    {r.targetMuscles?.length > 0 && <div><span className="text-xs font-semibold text-gray-500 block">Target Muscles</span>{r.targetMuscles.join(', ')}</div>}
                    {r.targetJoints?.length > 0 && <div><span className="text-xs font-semibold text-gray-500 block">Target Joints</span>{r.targetJoints.join(', ')}</div>}
                    {r.unit && <div><span className="text-xs font-semibold text-gray-500 block">Unit</span>{r.unit}</div>}
                    {r.testingProtocol && <div><span className="text-xs font-semibold text-gray-500 block">Testing Protocol</span>{r.testingProtocol}</div>}
                    {r.normalRangeMin !== undefined && <div><span className="text-xs font-semibold text-gray-500 block">Normal Range</span>{r.normalRangeMin} – {r.normalRangeMax}</div>}
                  </div>
                  {r.adminNote && (
                    <div className="text-sm bg-blue-50 border border-blue-100 rounded-lg p-3">
                      <span className="text-xs font-semibold text-blue-700 block mb-1">Previous Admin Note</span>
                      {r.adminNote}
                    </div>
                  )}
                  {r.status !== 'approved' && r.status !== 'rejected' && (
                    <div>
                      <label className="block text-xs font-semibold text-gray-700 mb-1">Admin Note (optional)</label>
                      <textarea
                        value={note}
                        onChange={e => setNote(e.target.value)}
                        rows={2}
                        placeholder="Add a note to the requester…"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm resize-none focus:outline-none focus:border-gray-900"
                      />
                      <div className="flex gap-2 mt-2">
                        <button
                          onClick={() => updateStatus(r.id, 'in-review')}
                          disabled={saving === r.id}
                          className="px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg text-xs font-medium disabled:opacity-50"
                        >
                          Mark In Review
                        </button>
                        <button
                          onClick={() => updateStatus(r.id, 'approved')}
                          disabled={saving === r.id}
                          className="px-3 py-1.5 bg-green-600 text-white rounded-lg text-xs font-medium disabled:opacity-50"
                        >
                          {saving === r.id ? 'Saving…' : 'Approve'}
                        </button>
                        <button
                          onClick={() => updateStatus(r.id, 'rejected')}
                          disabled={saving === r.id}
                          className="px-3 py-1.5 bg-red-50 text-red-700 border border-red-200 rounded-lg text-xs font-medium disabled:opacity-50"
                        >
                          Reject
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
