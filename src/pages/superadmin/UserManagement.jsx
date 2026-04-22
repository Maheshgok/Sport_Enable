import { useState, useEffect } from 'react'
import { collection, query, onSnapshot, doc, updateDoc, orderBy } from 'firebase/firestore'
import { db } from '../../firebase/config'

const ROLE_LABELS = { athlete: 'Athlete', physiotherapist: 'Physiotherapist', coach: 'Coach', caretaker: 'Caretaker', superadmin: 'Super Admin' }
const ROLE_ICONS = { athlete: '🏃', physiotherapist: '🏥', coach: '🎯', caretaker: '🤝', superadmin: '⚡' }

export default function UserManagement() {
  const [users, setUsers] = useState([])
  const [search, setSearch] = useState('')
  const [filterRole, setFilterRole] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')
  const [editUser, setEditUser] = useState(null)
  const [saving, setSaving] = useState(null)

  useEffect(() => {
    const q = query(collection(db, 'users'), orderBy('createdAt', 'desc'))
    return onSnapshot(q, (snap) => {
      setUsers(snap.docs.map((d) => ({ id: d.id, ...d.data() })))
    })
  }, [])

  const filtered = users.filter((u) => {
    const matchSearch = !search || u.displayName?.toLowerCase().includes(search.toLowerCase()) || u.email?.toLowerCase().includes(search.toLowerCase())
    const matchRole = filterRole === 'all' || u.role === filterRole
    const matchStatus = filterStatus === 'all' || u.status === filterStatus
    return matchSearch && matchRole && matchStatus
  })

  const saveEdit = async () => {
    setSaving(editUser.id)
    try {
      await updateDoc(doc(db, 'users', editUser.id), { role: editUser.role, status: editUser.status })
    } catch (e) { console.error(e) }
    setSaving(null)
    setEditUser(null)
  }

  const statusBadge = (status) => {
    const map = { approved: 'bg-green-100 text-green-700', pending: 'bg-amber-100 text-amber-700', rejected: 'bg-red-100 text-red-700' }
    return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${map[status] || 'bg-gray-100 text-gray-600'}`}>{status}</span>
  }

  const stats = {
    total: users.length,
    approved: users.filter(u => u.status === 'approved').length,
    pending: users.filter(u => u.status === 'pending').length,
    byRole: Object.entries(ROLE_LABELS).map(([k, v]) => ({ role: k, label: v, count: users.filter(u => u.role === k).length })).filter(r => r.count > 0),
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">User Management</h2>
        <p className="text-sm text-gray-500 mt-1">View, search, and edit all registered users.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div className="bg-white rounded-xl border border-gray-200 p-4"><div className="text-2xl font-bold text-gray-900">{stats.total}</div><div className="text-xs text-gray-500">Total Users</div></div>
        <div className="bg-white rounded-xl border border-green-200 p-4"><div className="text-2xl font-bold text-green-700">{stats.approved}</div><div className="text-xs text-gray-500">Active</div></div>
        <div className="bg-white rounded-xl border border-amber-200 p-4"><div className="text-2xl font-bold text-amber-700">{stats.pending}</div><div className="text-xs text-gray-500">Pending</div></div>
        {stats.byRole.map(r => (
          <div key={r.role} className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="text-2xl font-bold text-gray-900">{r.count}</div>
            <div className="text-xs text-gray-500">{ROLE_ICONS[r.role]} {r.label}s</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4">
        <input
          type="text"
          placeholder="Search name or email…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="flex-1 min-w-48 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900"
        />
        <select value={filterRole} onChange={e => setFilterRole(e.target.value)} className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
          <option value="all">All roles</option>
          {Object.entries(ROLE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
          <option value="all">All statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">User</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Role</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Joined</th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-10 text-center text-gray-400 text-sm">No users found</td></tr>
            ) : filtered.map((u) => (
              <tr key={u.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    {u.photoURL ? <img src={u.photoURL} alt="" className="w-8 h-8 rounded-full" /> : <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-xs font-medium text-gray-600">{u.displayName?.[0]}</div>}
                    <div>
                      <div className="font-medium text-gray-900">{u.displayName}</div>
                      <div className="text-xs text-gray-500">{u.email}</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded-full">{ROLE_ICONS[u.role]} {ROLE_LABELS[u.role] || u.role}</span>
                </td>
                <td className="px-4 py-3">{statusBadge(u.status)}</td>
                <td className="px-4 py-3 text-xs text-gray-400">{u.createdAt?.toDate ? u.createdAt.toDate().toLocaleDateString('en-GB') : '—'}</td>
                <td className="px-4 py-3 text-right">
                  <button onClick={() => setEditUser({ ...u })} className="text-xs text-gray-500 hover:text-gray-900 underline">Edit</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Edit modal */}
      {editUser && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Edit User — {editUser.displayName}</h3>
            <div className="space-y-3 mb-5">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Role</label>
                <select value={editUser.role} onChange={e => setEditUser(p => ({ ...p, role: e.target.value }))} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                  {Object.entries(ROLE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Status</label>
                <select value={editUser.status} onChange={e => setEditUser(p => ({ ...p, status: e.target.value }))} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>
            </div>
            <div className="flex gap-3">
              <button onClick={() => setEditUser(null)} className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm">Cancel</button>
              <button onClick={saveEdit} disabled={!!saving} className="flex-1 px-4 py-2 bg-gray-900 text-white rounded-lg text-sm disabled:opacity-50">
                {saving ? '…' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
