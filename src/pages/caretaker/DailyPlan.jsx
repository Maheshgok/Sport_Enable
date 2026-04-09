import { useState } from 'react'
import Card from '../../components/common/Card'
import Badge from '../../components/common/Badge'
import ProgressBar from '../../components/common/ProgressBar'

export default function DailyPlan({ athleteId, plan, onToggleTask }) {
  if (!plan) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Daily Plan</h2>
          <p className="text-gray-500">No plan available</p>
        </div>
      </div>
    )
  }

  const completedTasks = plan.tasks.filter(t => t.completed).length
  const totalTasks = plan.tasks.length
  const completionPercentage = Math.round((completedTasks / totalTasks) * 100)

  // Group tasks by type
  const tasksByType = plan.tasks.reduce((acc, task) => {
    if (!acc[task.type]) {
      acc[task.type] = []
    }
    acc[task.type].push(task)
    return acc
  }, {})

  const getTypeIcon = (type) => {
    switch (type) {
      case 'Exercise':
        return '💪'
      case 'Meal':
        return '🍽️'
      case 'Care':
        return '🏥'
      default:
        return '📋'
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'Exercise':
        return 'bg-gray-50 border-l-4 border-l-gray-900'
      case 'Meal':
        return 'bg-gray-50 border-l-4 border-l-gray-900'
      case 'Care':
        return 'bg-gray-50 border-l-4 border-l-gray-900'
      default:
        return 'bg-gray-50 border-l-4 border-l-gray-900'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Daily Plan - {plan.athleteName}</h2>
        <p className="text-gray-500">{plan.date}</p>
      </div>

      {/* Progress Overview */}
      <Card>
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-sm text-gray-500">Today's Progress</div>
            <div className="text-3xl font-semibold text-gray-900">
              {completedTasks} / {totalTasks} Tasks
            </div>
          </div>
          <div className="text-5xl">
            {completionPercentage === 100 ? '🎉' : '📋'}
          </div>
        </div>
        <ProgressBar 
          value={completionPercentage} 
          variant={completionPercentage === 100 ? 'success' : 'default'}
          showLabel
        />
      </Card>

      {/* Task Checklist by Type */}
      {Object.entries(tasksByType).map(([type, tasks]) => (
        <div key={type}>
          <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center space-x-2">
            <span>{getTypeIcon(type)}</span>
            <span>{type} Tasks ({tasks.filter(t => t.completed).length}/{tasks.length})</span>
          </h3>

          <div className="space-y-2">
            {tasks.map((task) => (
              <Card key={task.id} className={getTypeColor(type)}>
                <div className="flex items-start space-x-3">
                  {/* Checkbox */}
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => onToggleTask(athleteId, task.id)}
                    className="w-6 h-6 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 mt-1 cursor-pointer"
                  />

                  {/* Task Details */}
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center space-x-2">
                        <h4 className={`font-medium ${
                          task.completed ? 'text-gray-500 line-through' : 'text-gray-900'
                        }`}>
                          {task.title}
                        </h4>
                        {task.priority === 'high' && !task.completed && (
                          <Badge variant="warning">Priority</Badge>
                        )}
                      </div>
                      <span className={`text-sm font-medium ${
                        task.completed ? 'text-gray-400' : 'text-gray-600'
                      }`}>
                        {task.time}
                      </span>
                    </div>
                    <p className={`text-sm ${
                      task.completed ? 'text-gray-400' : 'text-gray-600'
                    }`}>
                      {task.description}
                    </p>
                    {task.completed && (
                      <div className="mt-2">
                        <Badge variant="success">✓ Completed</Badge>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      ))}

      {/* Summary Message */}
      {completionPercentage === 100 ? (
        <Card>
          <div className="flex items-center space-x-3 bg-gray-50 border border-gray-200 p-4 rounded-lg">
            <div className="text-3xl">🎉</div>
            <div>
              <div className="font-medium text-gray-900">All tasks completed!</div>
              <div className="text-sm text-gray-600">Great work today. All care tasks are done.</div>
            </div>
          </div>
        </Card>
      ) : (
        <Card>
          <div className="flex items-center space-x-3">
            <div className="text-2xl">💡</div>
            <div>
              <div className="font-medium text-gray-900">Keep going!</div>
              <div className="text-sm text-gray-600">
                {totalTasks - completedTasks} task{totalTasks - completedTasks !== 1 ? 's' : ''} remaining today.
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
