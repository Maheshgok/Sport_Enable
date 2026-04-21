import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'

const ROLES = [
  { value: 'athlete', label: 'Athlete', icon: '🏃', description: 'Track performance, assessments & recovery' },
  { value: 'physiotherapist', label: 'Physiotherapist', icon: '🏥', description: 'Manage cases, protocols & assessments' },
  { value: 'coach', label: 'Coach', icon: '🎯', description: 'Monitor athletes and team performance' },
  { value: 'caretaker', label: 'Caretaker', icon: '🤝', description: 'Support athlete daily plans & monitoring' },
]

const SPORTS = [
  'Football', 'Basketball', 'Tennis', 'Swimming', 'Running / Athletics',
  'Cycling', 'Rugby', 'Cricket', 'Hockey', 'Volleyball', 'Other'
]

const PHYSIO_SPECIALIZATIONS = [
  'Sports Physiotherapy', 'Orthopedic', 'Neurological', 'Pediatric', 'General'
]

export default function CompleteProfile() {
  const { user, saveProfile, logout } = useAuth()
  const [selectedRole, setSelectedRole] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    fullName: user?.displayName || '',
    phone: '',
    // Athlete
    sport: '',
    teamClub: '',
    dateOfBirth: '',
    // Physiotherapist
    licenseNumber: '',
    specialization: '',
    yearsExperience: '',
    // Coach
    coachSport: '',
    coachTeam: '',
    coachExperience: '',
    // Caretaker
    organization: '',
    relationship: '',
  })

  const set = (field) => (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!selectedRole) { setError('Please select a role.'); return }
    if (!form.fullName.trim()) { setError('Please enter your full name.'); return }
    if (!form.phone.trim()) { setError('Please enter your phone number.'); return }
    setError('')
    setSaving(true)
    try {
      const roleData = buildRoleData()
      await saveProfile({ fullName: form.fullName, phone: form.phone, role: selectedRole, ...roleData })
    } catch (err) {
      setError('Failed to save profile. Please try again.')
      console.error(err)
    } finally {
      setSaving(false)
    }
  }

  const buildRoleData = () => {
    switch (selectedRole) {
      case 'athlete':
        return { sport: form.sport, teamClub: form.teamClub, dateOfBirth: form.dateOfBirth }
      case 'physiotherapist':
        return { licenseNumber: form.licenseNumber, specialization: form.specialization, yearsExperience: form.yearsExperience }
      case 'coach':
        return { sport: form.coachSport, teamClub: form.coachTeam, yearsExperience: form.coachExperience }
      case 'caretaker':
        return { organization: form.organization, relationship: form.relationship }
      default:
        return {}
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-start p-4 pt-10">
      <div className="w-full max-w-xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-1">Moove</h1>
          <p className="text-gray-500 text-sm">Complete your profile to request access</p>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8">
          {/* Google account info */}
          <div className="flex items-center gap-3 mb-6 p-3 bg-gray-50 rounded-lg">
            {user?.photoURL && (
              <img src={user.photoURL} alt="" className="w-10 h-10 rounded-full" />
            )}
            <div>
              <div className="text-sm font-medium text-gray-900">{user?.displayName}</div>
              <div className="text-xs text-gray-500">{user?.email}</div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic info */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Basic Information</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                <input
                  type="text"
                  value={form.fullName}
                  onChange={set('fullName')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900"
                  placeholder="Your full name"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number *</label>
                <input
                  type="tel"
                  value={form.phone}
                  onChange={set('phone')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900"
                  placeholder="+1 000 000 0000"
                  required
                />
              </div>
            </div>

            {/* Role selection */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">I am a… *</h3>
              <div className="grid grid-cols-2 gap-3">
                {ROLES.map((role) => (
                  <button
                    key={role.value}
                    type="button"
                    onClick={() => setSelectedRole(role.value)}
                    className={`text-left p-4 rounded-xl border-2 transition-all ${
                      selectedRole === role.value
                        ? 'border-gray-900 bg-gray-900 text-white'
                        : 'border-gray-200 bg-white text-gray-700 hover:border-gray-400'
                    }`}
                  >
                    <div className="text-2xl mb-1">{role.icon}</div>
                    <div className="font-medium text-sm">{role.label}</div>
                    <div className={`text-xs mt-1 ${selectedRole === role.value ? 'text-gray-300' : 'text-gray-400'}`}>
                      {role.description}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Role-specific fields */}
            {selectedRole === 'athlete' && (
              <div className="space-y-4 pt-2">
                <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Athlete Details</h3>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Primary Sport</label>
                  <select value={form.sport} onChange={set('sport')} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900">
                    <option value="">Select sport…</option>
                    {SPORTS.map((s) => <option key={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Team / Club</label>
                  <input type="text" value={form.teamClub} onChange={set('teamClub')} placeholder="Optional" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
                  <input type="date" value={form.dateOfBirth} onChange={set('dateOfBirth')} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900" />
                </div>
              </div>
            )}

            {selectedRole === 'physiotherapist' && (
              <div className="space-y-4 pt-2">
                <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Professional Details</h3>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">License / Registration Number</label>
                  <input type="text" value={form.licenseNumber} onChange={set('licenseNumber')} placeholder="e.g. HCPC12345" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Specialization</label>
                  <select value={form.specialization} onChange={set('specialization')} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900">
                    <option value="">Select…</option>
                    {PHYSIO_SPECIALIZATIONS.map((s) => <option key={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Years of Experience</label>
                  <input type="number" min="0" max="50" value={form.yearsExperience} onChange={set('yearsExperience')} placeholder="e.g. 5" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900" />
                </div>
              </div>
            )}

            {selectedRole === 'coach' && (
              <div className="space-y-4 pt-2">
                <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Coaching Details</h3>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Sport</label>
                  <select value={form.coachSport} onChange={set('coachSport')} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900">
                    <option value="">Select sport…</option>
                    {SPORTS.map((s) => <option key={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Team / Club</label>
                  <input type="text" value={form.coachTeam} onChange={set('coachTeam')} placeholder="Optional" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Years of Experience</label>
                  <input type="number" min="0" max="50" value={form.coachExperience} onChange={set('coachExperience')} placeholder="e.g. 8" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900" />
                </div>
              </div>
            )}

            {selectedRole === 'caretaker' && (
              <div className="space-y-4 pt-2">
                <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Caretaker Details</h3>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Organisation / Club</label>
                  <input type="text" value={form.organization} onChange={set('organization')} placeholder="e.g. City FC Academy" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Relationship to Athletes</label>
                  <select value={form.relationship} onChange={set('relationship')} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900">
                    <option value="">Select…</option>
                    <option>Parent / Guardian</option>
                    <option>Sports Medical Staff</option>
                    <option>Team Manager</option>
                    <option>Strength & Conditioning Coach</option>
                    <option>Other</option>
                  </select>
                </div>
              </div>
            )}

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={saving || !selectedRole}
              className="w-full py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {saving ? 'Submitting…' : 'Submit Access Request'}
            </button>
          </form>
        </div>

        <button onClick={logout} className="mt-4 w-full text-center text-sm text-gray-400 hover:text-gray-600">
          Sign out and use a different account
        </button>
      </div>
    </div>
  )
}
