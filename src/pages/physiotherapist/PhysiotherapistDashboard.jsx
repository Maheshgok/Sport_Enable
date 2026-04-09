import { useState } from 'react'
import Card from '../../components/common/Card'
import CaseList from './CaseList'
import CaseDetail from './CaseDetail'
import { athleteCases, caseAssessments } from '../../data/mockPhysioData'

export default function PhysiotherapistDashboard({ currentView, setCurrentView }) {
  const [internalView, setInternalView] = useState('list') // 'list' or 'detail'
  const [selectedCaseId, setSelectedCaseId] = useState(null)
  
  // Local state for case updates (simulating backend updates)
  const [cases, setCases] = useState(athleteCases)
  const [assessments, setAssessments] = useState(caseAssessments)

  const handleSelectCase = (caseId) => {
    setSelectedCaseId(caseId)
    setInternalView('detail')
  }

  const handleBackToList = () => {
    setInternalView('list')
    setSelectedCaseId(null)
  }

  const handleUpdateCase = (caseId, updates) => {
    // Update assessments with new diagnosis and exercises
    setAssessments(prev => ({
      ...prev,
      [caseId]: {
        ...prev[caseId],
        diagnosis: updates.diagnosis,
        assignedExercises: updates.assignedExercises
      }
    }))

    // Update case last update date
    setCases(prev => prev.map(c => 
      c.id === caseId 
        ? { ...c, lastUpdate: new Date().toISOString().split('T')[0] }
        : c
    ))
  }

  const selectedCase = cases.find(c => c.id === selectedCaseId)
  const selectedAssessment = assessments[selectedCaseId]

  // Dashboard view
  if (currentView === 'dashboard') {
    const activeCases = cases.filter(c => c.status === 'active').length
    const completedCases = cases.filter(c => c.status === 'completed').length
    const pendingReviews = cases.filter(c => c.priority === 'high').length

    return (
      <div className="space-y-8">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Physiotherapist Dashboard</h2>
          <p className="text-gray-600">Overview of your athlete cases</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <div className="text-sm text-gray-500 mb-2">Active Cases</div>
            <div className="text-3xl font-semibold text-gray-900">{activeCases}</div>
          </Card>
          <Card>
            <div className="text-sm text-gray-500 mb-2">Completed</div>
            <div className="text-3xl font-semibold text-gray-900">{completedCases}</div>
          </Card>
          <Card>
            <div className="text-sm text-gray-500 mb-2">Pending Reviews</div>
            <div className="text-3xl font-semibold text-gray-900">{pendingReviews}</div>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card title="Quick Actions">
          <div className="grid grid-cols-2 gap-6">
            <button
              onClick={() => setCurrentView('cases')}
              className="p-6 bg-white border border-gray-200 rounded-lg text-left hover:border-gray-900"
            >
              <div className="text-2xl mb-3">🏥</div>
              <div className="font-medium text-gray-900 mb-1">View All Cases</div>
              <div className="text-sm text-gray-600">Manage athlete assessments</div>
            </button>
            <button
              className="p-6 bg-white border border-gray-200 rounded-lg text-left hover:border-gray-900"
            >
              <div className="text-2xl mb-3">📊</div>
              <div className="font-medium text-gray-900 mb-1">Reports</div>
              <div className="text-sm text-gray-600">View analytics and trends</div>
            </button>
          </div>
        </Card>
      </div>
    )
  }

  // Cases view
  if (currentView === 'cases') {
    return (
      <div>
        {internalView === 'list' ? (
          <CaseList 
            cases={cases} 
            onSelectCase={handleSelectCase}
          />
        ) : (
          <CaseDetail
            athleteCase={selectedCase}
            assessment={selectedAssessment}
            onBack={handleBackToList}
            onUpdate={handleUpdateCase}
          />
        )}
      </div>
    )
  }
}
