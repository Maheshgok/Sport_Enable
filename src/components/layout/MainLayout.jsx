import Topbar from './Topbar'
import Sidebar from './Sidebar'

export default function MainLayout({ children, currentRole, currentView, onViewChange }) {
  return (
    <div className="h-screen flex flex-col">
      {/* Topbar */}
      <Topbar currentRole={currentRole} />
      
      {/* Main container with sidebar and content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar currentRole={currentRole} currentView={currentView} onViewChange={onViewChange} />
        
        {/* Main content area */}
        <main className="flex-1 overflow-y-auto bg-gray-50 p-8">
          {children}
        </main>
      </div>
    </div>
  )
}
