import { useState, useEffect } from 'react'
import Card from '../../components/common/Card'
import Badge from '../../components/common/Badge'
import { Play, Search, Filter, Clock, Users, FileText, Video } from 'lucide-react'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080'

export default function AssessmentPrompts({ currentUser }) {
  const [prompts, setPrompts] = useState({})
  const [categories, setCategories] = useState([])
  const [selectedCategory, setSelectedCategory] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [executingPrompt, setExecutingPrompt] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadPrompts()
  }, [])

  const loadPrompts = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_BASE_URL}/api/prompts`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setPrompts(data.prompts)

        // Extract categories
        const categoryList = Object.keys(data.prompts).sort()
        setCategories(categoryList)
      }
    } catch (error) {
      console.error('Error loading prompts:', error)
    }
  }

  const executePrompt = async (promptCode) => {
    const athleteId = prompt('Enter athlete ID to execute assessment:')
    if (!athleteId) return

    setExecutingPrompt(promptCode)
    setLoading(true)

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_BASE_URL}/api/prompts/${promptCode}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ athlete_id: athleteId })
      })

      if (response.ok) {
        const data = await response.json()
        alert(`Assessment execution started! Execution ID: ${data.execution.execution_id}`)
      } else {
        const error = await response.json()
        alert(error.error || 'Failed to execute assessment')
      }
    } catch (error) {
      console.error('Error executing assessment:', error)
      alert('Failed to execute assessment')
    } finally {
      setExecutingPrompt(null)
      setLoading(false)
    }
  }

  const filteredPrompts = () => {
    let filtered = { ...prompts }

    // Filter by category
    if (selectedCategory) {
      filtered = { [selectedCategory]: prompts[selectedCategory] || [] }
    }

    // Filter by search term
    if (searchTerm) {
      Object.keys(filtered).forEach(category => {
        filtered[category] = filtered[category].filter(prompt =>
          prompt.prompt_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          prompt.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          prompt.clinical_category.toLowerCase().includes(searchTerm.toLowerCase())
        )
      })
    }

    return filtered
  }

  const getClinicalBadgeVariant = (category) => {
    const variants = {
      'musculoskeletal': 'primary',
      'neurological': 'secondary',
      'cardiovascular': 'success',
      'respiratory': 'warning',
      'sports_performance': 'info'
    }
    return variants[category] || 'default'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Clinical Assessment Library</h1>
          <p className="text-gray-600">Select from standardized clinical assessments for automated video analysis</p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search assessments..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="sm:w-64">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
        </div>
      </Card>

      {/* Assessment Categories */}
      {Object.entries(filteredPrompts()).map(([category, categoryPrompts]) => (
        categoryPrompts.length > 0 && (
          <div key={category}>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">{category}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {categoryPrompts.map(prompt => (
                <Card key={prompt.prompt_id} className="hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {prompt.prompt_name}
                      </h3>
                      <p className="text-sm text-gray-600 mb-2">{prompt.description}</p>
                    </div>
                    <Badge variant={getClinicalBadgeVariant(prompt.clinical_category)}>
                      {prompt.clinical_category}
                    </Badge>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Users className="w-4 h-4" />
                      <span>{prompt.target_population}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Clock className="w-4 h-4" />
                      <span>{prompt.estimated_duration_minutes} min</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Video className="w-4 h-4" />
                      <span>{prompt.required_views?.join(', ') || 'front'}</span>
                    </div>
                  </div>

                  {prompt.clinical_indications && (
                    <div className="mb-4">
                      <p className="text-xs text-gray-500 mb-1">Clinical Indications:</p>
                      <p className="text-sm text-gray-700">{prompt.clinical_indications}</p>
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <button
                      onClick={() => executePrompt(prompt.prompt_code)}
                      disabled={executingPrompt === prompt.prompt_code || loading}
                      className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Play className="w-4 h-4" />
                      <span>
                        {executingPrompt === prompt.prompt_code ? 'Executing...' : 'Execute Assessment'}
                      </span>
                    </button>
                    <div className="text-xs text-gray-500">
                      {prompt.creator_name}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )
      ))}

      {/* Empty State */}
      {Object.keys(filteredPrompts()).length === 0 && (
        <Card>
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No assessments found</h3>
            <p className="text-gray-600">
              {searchTerm || selectedCategory
                ? 'Try adjusting your search or filter criteria.'
                : 'No clinical assessments are currently available.'
              }
            </p>
          </div>
        </Card>
      )}
    </div>
  )
}