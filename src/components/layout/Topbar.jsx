import { mockUser } from '../../data/mockData'

export default function Topbar({ currentRole, onRoleChange }) {
  const user = mockUser[currentRole]
  
  const roles = ['athlete', 'physiotherapist', 'coach', 'caretaker']

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-6">
          <h1 className="text-xl font-semibold text-gray-900">Moove</h1>
          <span className="text-sm text-gray-500">
            {currentRole.charAt(0).toUpperCase() + currentRole.slice(1)}
          </span>
        </div>

        <div className="flex items-center space-x-6">
          {/* Role Switcher */}
          <select
            value={currentRole}
            onChange={(e) => onRoleChange(e.target.value)}
            className="px-3 py-2 text-sm border border-gray-200 rounded-md bg-white text-gray-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          >
            {roles.map((role) => (
              <option key={role} value={role}>
                {role.charAt(0).toUpperCase() + role.slice(1)}
              </option>
            ))}
          </select>

          {/* User Info */}
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">{user.name}</div>
              <div className="text-xs text-gray-500">{user.email}</div>
            </div>
            <div className="w-9 h-9 bg-gray-900 rounded-full flex items-center justify-center text-white text-sm font-medium">
              {user.avatar}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
