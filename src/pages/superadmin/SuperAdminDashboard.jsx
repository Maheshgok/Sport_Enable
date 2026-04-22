import { useState, useEffect } from 'react'
import { collection, query, where, onSnapshot, doc, updateDoc, orderBy } from 'firebase/firestore'
import { db } from '../../firebase/config'
import { useAuth } from '../../context/AuthContext'
import UserManagement from './UserManagement'
import PhysioRequests from './PhysioRequests'
import MetaAnalysis from './MetaAnalysis'

const ROLE_LABELS = {
  athlete: 'Athlete',
  physiotherapist: 'Physiotherapist',
  coach: 'Coach',
  caretaker: 'Caretaker',
  superadmin: 'Super Admin',
}

const ROLE_ICONS = {
  athlete: '🏃',
  physiotherapist: '🏥',
  coach: '🎯',
  caretaker: '🤝',
  superadmin: '⚡',
}

const STATUS_TABS = ['pending', 'approved', 'rejected']

const NAV_ITEMS = [
  { id: 'onboarding', label: 'Onboarding', icon: '📋' },
  { id: 'users', label: 'User Management', icon: '👥' },
  { id: 'physio-requests', label: 'Physio Requests', icon: '🏥' },
  { id: 'meta', label: 'Meta Analysis', icon: '📊' },
]

function OnboardingPanel({ user: authUser }) {
  const [activeTab, setActiveTab] = useState('pending')
  const [users, setUsers] = useState({ pending: [], approved: [], rejected: [] })
  const [processing, setProcessing] = useState(null)
  const [reviewNote, setReviewNote] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [actionType, setActionType] = useState(null)

  useEffect(() => {
    const unsubscribers = STATUS_TABS.map((status) => {
      const q = query(collection(db, 'users'), where('status', '==', status), orderBy('createdAt', 'desc'))
      return onSnapshot(q, (snapshot) => {
        const data = snapshot.docs.map((d) => ({ id: d.id, ...d.data() }))
        setUsers((prev) => ({ ...prev, [status]: data }))
      })
    })
    return () => unsubscribers.forEach((u) => u())
  }, [])

  const openAction = (usr, type) => { setSelectedUser(usr); setActionType(type); setReviewNote('') }

  const confirmAction = async () => {
    if (!selectedUser) return
    setProcessing(selectedUser.uid)
    try {
      await updateDoc(doc(db, 'users', selectedUser.uid), {
        status: actionType === 'approve' ? 'approved' : 'rejected',
        reviewNote: reviewNote.trim(),
        reviewedBy: authUser?.uid,
        reviewedAt: new Date(),
      })
    } catch (err) { console.error(err) }
    setProcessing(null)
    setSelectedUser(null)
  }

  const pendingCount = users.pending.length

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">Onboarding Requests</h2>
        <p className="text-gray-500 text-sm mt-1">Review and approve sign-up requests from new users.</p>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: 'Pending', count: users.pending.length, color: 'bg-amber-50 border-amber-200 text-amber-700' },
          { label: 'Approved', count: users.approved.length, color: 'bg-green-50 border-green-200 text-green-700' },
          { label: 'Rejected', count: users.rejected.length, color: 'bg-red-50 border-red-200 text-red-700' },
        ].map((stat) => (
          <div key={stat.label} className={`rounded-xl border p-4 ${stat.color}`}>
            <div className="text-2xl font-bold">{stat.count}</div>
            <div className="text-sm font-medium">{stat.label}</div>
          </div>
        ))}
      </div>

      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 mb-6 w-fit">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors capitalize flex items-center gap-2 ${
              activeTab === tab ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab}
            {tab === 'pending' && pendingCount > 0 && (
              <span className="w-5 h-5 bg-amber-500 text-white text-xs rounded-full flex items-center justify-center">{pendingCount}</span>
            )}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {users[activeTab].length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <div className="text-4xl mb-3">📭</div>
            <p className="text-sm">No {activeTab} requests</p>
          </div>
        ) : users[activeTab].map((usr) => (
          <div key={usr.uid || usr.id} className="bg-white rounded-xl border border-gray-200 p-5 flex items-start justify-between gap-4">
            <div className="flex items-start gap-4">
              {usr.photoURL ? (
                <img src={usr.photoURL} alt="" className="w-11 h-11 rounded-full shrink-0" />
              ) : (
                <div className="w-11 h-11 bg-gray-100 rounded-full flex items-center justify-center text-lg shrink-0">
                  {ROLE_ICONS[usr.role] || '👤'}
                </div>
              )}
              <div>
                <div className="font-medium text-gray-900">{usr.displayName}</div>
                <div className="text-sm text-gray-500">{usr.email}</div>
                <div className="flex flex-wrap gap-2 mt-2">
                  <span className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded-full font-medium">
                    {ROLE_ICONS[usr.role]} {ROLE_LABELS[usr.role] || usr.role}
                  </span>
                  {usr.sport && <span className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full">{usr.sport}</span>}
                  {usr.specialization && <span className="px-2 py-0.5 bg-purple-50 text-purple-700 text-xs rounded-full">{usr.specialization}</span>}
                  {usr.teamClub && <span className="px-2 py-0.5 bg-gray-50 text-gray-600 text-xs rounded-full">{usr.teamClub}</span>}
                  {usr.licenseNumber && <span className="px-2 py-0.5 bg-gray-50 text-gray-600 text-xs rounded-full">License: {usr.licenseNumber}</span>}
                  {usr.phone && <span className="px-2 py-0.5 bg-gray-50 text-gray-600 text-xs rounded-full">{usr.phone}</span>}
                </div>
                {usr.reviewNote && <div className="mt-2 text-xs text-gray-400 italic">Note: {usr.reviewNote}</div>}
                <div className="mt-1 text-xs text-gray-400">
                  {usr.createdAt?.toDate ? usr.createdAt.toDate().toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : 'Just now'}
                </div>
              </div>
            </div>

            {activeTab === 'pending' && (
              <div className="flex gap-2 shrink-0">
                <button onClick={() => openAction(usr, 'reject')} disabled={processing === usr.uid} className="px-3 py-1.5 text-sm border border-red-200 text-red-600 rounded-lg hover:bg-red-50 disabled:opacity-50">Reject</button>
                <button onClick={() => openAction(usr, 'approve')} disabled={processing === usr.uid} className="px-3 py-1.5 text-sm bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50">{processing === usr.uid ? '…' : 'Approve'}</button>
              </div>
            )}
            {activeTab === 'approved' && <span className="shrink-0 px-2.5 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">Approved</span>}
            {activeTab === 'rejected' && (
              <div className="shrink-0 flex flex-col items-end gap-1">
                <span className="px-2.5 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-full">Rejected</span>
                <button onClick={() => openAction(usr, 'approve')} className="text-xs text-gray-400 hover:text-gray-700 underline">Re-approve</button>
              </div>
            )}
          </div>
        ))}
      </div>

      {selectedUser && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {actionType === 'approve' ? '✅ Approve Access' : '❌ Reject Request'}
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              {actionType === 'approve'
                ? `Grant ${selectedUser.displayName} access as a ${ROLE_LABELS[selectedUser.role] || selectedUser.role}.`
                : `Deny access for ${selectedUser.displayName}.`}
            </p>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Note (optional)</label>
              <textarea value={reviewNote} onChange={(e) => setReviewNote(e.target.value)} rows={3} placeholder="Add a note…" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900 resize-none" />
            </div>
            <div className="flex gap-3">
              <button onClick={() => setSelectedUser(null)} className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50">Cancel</button>
              <button onClick={confirmAction} disabled={!!processing} className={`flex-1 px-4 py-2 text-white rounded-lg text-sm font-medium disabled:opacity-50 ${actionType === 'approve' ? 'bg-gray-900 hover:bg-gray-800' : 'bg-red-600 hover:bg-red-700'}`}>
                {processing ? '…' : actionType === 'approve' ? 'Approve' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function SuperAdminDashboard() {
  const { user, userProfile, logout } = useAuth()
  const [activePanel, setActivePanel] = useState('onboarding')
  const [pendingCount, setPendingCount] = useState(0)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    const q = query(collection(db, 'users'), where('status', '==', 'pending'))
    return onSnapshot(q, (snap) => setPendingCount(snap.size))
  }, [])

  const panels = {
    onboarding: <OnboardingPanel user={user} />,
    users: <UserManagement />,
    'physio-requests': <PhysioRequests />,
    meta: <MetaAnalysis />,
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Top header */}
      <div className="bg-white border-b border-gray-200 px-4 md:px-6 py-4 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="md:hidden p-1 rounded text-gray-500 hover:text-gray-900">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
          </button>
          <h1 className="text-lg font-semibold text-gray-900">Moove</h1>
          <span className="hidden sm:inline px-2.5 py-0.5 bg-gray-900 text-white text-xs font-medium rounded-full">Super Admin</span>
        </div>
        <div className="flex items-center gap-3">
          {userProfile?.photoURL || user?.photoURL ? (
            <img src={userProfile?.photoURL || user?.photoURL} alt="" className="w-8 h-8 rounded-full" />
          ) : (
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-sm font-medium text-gray-600">
              {(userProfile?.displayName || user?.displayName)?.[0]}
            </div>
          )}
          <span className="hidden sm:block text-sm text-gray-700">{userProfile?.displayName || user?.displayName}</span>
          <button onClick={logout} className="text-sm text-gray-500 hover:text-gray-900">Sign out</button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className={`${sidebarOpen ? 'block' : 'hidden'} md:block w-56 bg-white border-r border-gray-200 flex-shrink-0 overflow-y-auto`}>
          <nav className="p-4 space-y-1">
            {NAV_ITEMS.map((item) => (
              <button
                key={item.id}
                onClick={() => { setActivePanel(item.id); setSidebarOpen(false) }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors text-left ${
                  activePanel === item.id ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <span>{item.icon}</span>
                <span className="flex-1">{item.label}</span>
                {item.id === 'onboarding' && pendingCount > 0 && (
                  <span className={`w-5 h-5 text-xs rounded-full flex items-center justify-center font-semibold ${activePanel === item.id ? 'bg-white text-gray-900' : 'bg-amber-500 text-white'}`}>{pendingCount}</span>
                )}
              </button>
            ))}
          </nav>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-5xl mx-auto">
            {panels[activePanel]}
          </div>
        </main>
      </div>
    </div>
  )
}
