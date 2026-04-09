export default function Sidebar({ currentRole, currentView, onViewChange }) {
  // Map menu items to actual views that exist
  const menuItems = {
    athlete: [
      { label: 'Dashboard', icon: '📊', view: 'dashboard' },
      { label: 'Assessment', icon: '📹', view: 'assessment' },
      { label: 'Recommendations', icon: '💪', view: 'recommendations' },
      { label: 'Progress', icon: '📈', view: 'progress' },
      { label: 'Video Analysis', icon: '🎥', view: 'video-analysis' }
    ],
    physiotherapist: [
      { label: 'Dashboard', icon: '📊', view: 'dashboard' },
      { label: 'Cases', icon: '🏥', view: 'cases' },
      { label: 'Video Analysis', icon: '🎥', view: 'video-analysis' }
    ],
    coach: [
      { label: 'Dashboard', icon: '📊', view: 'dashboard' },
      { label: 'Athletes', icon: '🏃', view: 'athletes' },
      { label: 'Video Analysis', icon: '🎥', view: 'video-analysis' }
    ],
    caretaker: [
      { label: 'Dashboard', icon: '📊', view: 'dashboard' },
      { label: 'Daily Plans', icon: '✅', view: 'plans' },
      { label: 'Monitoring', icon: '📈', view: 'monitoring' },
      { label: 'Video Analysis', icon: '🎥', view: 'video-analysis' }
    ]
  }

  const items = menuItems[currentRole] || menuItems.athlete

  return (
    <div className="w-64 bg-white border-r border-gray-200 h-full p-6">
      <nav className="space-y-1">
        {items.map((item) => (
          <button
            key={item.view}
            onClick={() => onViewChange(item.view)}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-md text-left text-sm ${
              currentView === item.view
                ? 'bg-gray-900 text-white'
                : 'text-gray-700 hover:bg-gray-50'
            }`}
          >
            <span className="text-lg">{item.icon}</span>
            <span className="font-medium">{item.label}</span>
          </button>
        ))}
      </nav>
    </div>
  )
}
