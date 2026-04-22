import { useState, useEffect } from 'react'
import { collection, query, onSnapshot, orderBy, where, Timestamp } from 'firebase/firestore'
import { db } from '../../firebase/config'

function StatCard({ label, value, sub, color = 'border-gray-200', textColor = 'text-gray-900' }) {
  return (
    <div className={`bg-white rounded-xl border ${color} p-4`}>
      <div className={`text-3xl font-bold ${textColor}`}>{value}</div>
      <div className="text-sm text-gray-700 font-medium mt-0.5">{label}</div>
      {sub && <div className="text-xs text-gray-400 mt-0.5">{sub}</div>}
    </div>
  )
}

export default function MetaAnalysis() {
  const [users, setUsers] = useState([])
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsub1 = onSnapshot(query(collection(db, 'users'), orderBy('createdAt', 'desc')), (snap) => {
      setUsers(snap.docs.map(d => ({ id: d.id, ...d.data() })))
      setLoading(false)
    })
    const unsub2 = onSnapshot(query(collection(db, 'physio_requests'), orderBy('createdAt', 'desc')), (snap) => {
      setRequests(snap.docs.map(d => ({ id: d.id, ...d.data() })))
    })
    return () => { unsub1(); unsub2() }
  }, [])

  // User stats
  const totalUsers = users.length
  const approved = users.filter(u => u.status === 'approved').length
  const pending = users.filter(u => u.status === 'pending').length
  const rejected = users.filter(u => u.status === 'rejected').length
  const byRole = ['athlete', 'physiotherapist', 'coach', 'caretaker', 'superadmin'].map(role => ({
    role,
    count: users.filter(u => u.role === role).length,
  })).filter(r => r.count > 0)

  // Signup trends — last 7 days
  const now = Date.now()
  const dayMs = 86400000
  const last7 = Array.from({ length: 7 }, (_, i) => {
    const day = new Date(now - (6 - i) * dayMs)
    const label = day.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric' })
    const start = new Date(day); start.setHours(0, 0, 0, 0)
    const end = new Date(day); end.setHours(23, 59, 59, 999)
    const count = users.filter(u => {
      const ts = u.createdAt?.toDate ? u.createdAt.toDate().getTime() : null
      return ts && ts >= start.getTime() && ts <= end.getTime()
    }).length
    return { label, count }
  })
  const maxBar = Math.max(...last7.map(d => d.count), 1)

  // Request stats
  const pendingReqs = requests.filter(r => r.status === 'pending').length
  const approvedReqs = requests.filter(r => r.status === 'approved').length
  const exerciseReqs = requests.filter(r => r.type === 'exercise').length
  const baselineReqs = requests.filter(r => r.type === 'baseline').length

  const ROLE_ICONS = { athlete: '🏃', physiotherapist: '🏥', coach: '🎯', caretaker: '🤝', superadmin: '⚡' }
  const ROLE_LABELS = { athlete: 'Athletes', physiotherapist: 'Physiotherapists', coach: 'Coaches', caretaker: 'Caretakers', superadmin: 'Super Admins' }

  if (loading) {
    return <div className="flex items-center justify-center h-48 text-gray-400 text-sm">Loading analytics…</div>
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">Meta Analysis</h2>
        <p className="text-sm text-gray-500 mt-1">Platform-wide aggregate statistics and trends.</p>
      </div>

      {/* User overview */}
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Users</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <StatCard label="Total Users" value={totalUsers} />
        <StatCard label="Active" value={approved} color="border-green-200" textColor="text-green-700" />
        <StatCard label="Pending Approval" value={pending} color="border-amber-200" textColor="text-amber-700" />
        <StatCard label="Rejected" value={rejected} color="border-red-200" textColor="text-red-700" />
      </div>

      {/* Role breakdown */}
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">By Role</h3>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        {['athlete', 'physiotherapist', 'coach', 'caretaker', 'superadmin'].map(role => (
          <div key={role} className="bg-white rounded-xl border border-gray-200 p-4 text-center">
            <div className="text-2xl mb-1">{ROLE_ICONS[role]}</div>
            <div className="text-2xl font-bold text-gray-900">{users.filter(u => u.role === role).length}</div>
            <div className="text-xs text-gray-500">{ROLE_LABELS[role]}</div>
          </div>
        ))}
      </div>

      {/* Signup trend */}
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Signups — Last 7 Days</h3>
      <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6">
        <div className="flex items-end gap-2 h-32">
          {last7.map((d, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-1">
              <div className="text-xs text-gray-500">{d.count || ''}</div>
              <div
                className="w-full bg-gray-900 rounded-t"
                style={{ height: `${Math.round((d.count / maxBar) * 100)}%`, minHeight: d.count > 0 ? 4 : 0 }}
              />
            </div>
          ))}
        </div>
        <div className="flex gap-2 mt-2">
          {last7.map((d, i) => (
            <div key={i} className="flex-1 text-center text-xs text-gray-400">{d.label}</div>
          ))}
        </div>
      </div>

      {/* Physio requests */}
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Physio Requests</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <StatCard label="Total Requests" value={requests.length} />
        <StatCard label="Pending" value={pendingReqs} color="border-amber-200" textColor="text-amber-700" />
        <StatCard label="Approved" value={approvedReqs} color="border-green-200" textColor="text-green-700" />
        <StatCard label="Exercise / Baseline" value={`${exerciseReqs} / ${baselineReqs}`} sub="request types" />
      </div>

      {/* Top requesters */}
      {requests.length > 0 && (() => {
        const counts = {}
        requests.forEach(r => {
          const key = r.requesterEmail || r.requesterUid
          if (!key) return
          counts[key] = (counts[key] || { name: r.requesterName, email: r.requesterEmail, count: 0 })
          counts[key].count++
        })
        const top = Object.values(counts).sort((a, b) => b.count - a.count).slice(0, 5)
        return (
          <>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Top Requesters</h3>
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden mb-6">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Name</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Email</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500">Requests</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {top.map((r, i) => (
                    <tr key={i} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-gray-900">{r.name || '—'}</td>
                      <td className="px-4 py-3 text-gray-500 text-xs">{r.email}</td>
                      <td className="px-4 py-3 text-right font-semibold text-gray-900">{r.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )
      })()}
    </div>
  )
}
