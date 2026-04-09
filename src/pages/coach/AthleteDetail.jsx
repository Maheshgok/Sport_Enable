import { useState } from 'react'
import Card from '../../components/common/Card'
import Badge from '../../components/common/Badge'

export default function AthleteDetail({ athlete, details, onBack, onAddComment }) {
  const [newComment, setNewComment] = useState('')

  const handleSubmitComment = () => {
    if (newComment.trim()) {
      onAddComment(athlete.id, newComment)
      setNewComment('')
      alert('Comment added successfully!')
    }
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <button
        onClick={onBack}
        className="flex items-center space-x-2 text-gray-900 hover:text-gray-700 font-medium"
      >
        <span>←</span>
        <span>Back to Athlete Overview</span>
      </button>

      {/* Athlete Header */}
      <Card>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-gray-900 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              {athlete.avatar}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{athlete.name}</h2>
              <p className="text-gray-500">{athlete.sport} - {athlete.position} - Age {athlete.age}</p>
              <div className="flex items-center space-x-3 mt-1">
                <Badge variant={
                  athlete.status === 'active' ? 'active' :
                  athlete.status === 'recovering' ? 'warning' :
                  'success'
                }>
                  {athlete.status}
                </Badge>
                <span className="text-sm text-gray-500">Physio: {athlete.physio}</span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Training Status</div>
            <div className="text-lg font-semibold text-gray-900">{athlete.trainingStatus}</div>
            <div className="text-sm text-gray-500 mt-1">Recovery: {athlete.recoveryProgress}%</div>
          </div>
        </div>
      </Card>

      {/* Current Condition */}
      <Card title="Current Condition">
        <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
          <p className="text-gray-900">{athlete.condition}</p>
          <div className="mt-2 text-sm text-gray-500">Last updated: {athlete.lastUpdate}</div>
        </div>
      </Card>

      {/* Insights (Read-only) */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">📊 Clinical Insights</h3>
        {details?.insights && details.insights.length > 0 ? (
          <div className="space-y-3">
            {details.insights.map((insight) => (
              <Card key={insight.id}>
                <div className="flex items-start space-x-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-medium text-gray-900">{insight.title}</h4>
                      <Badge variant={
                        insight.severity === 'moderate' ? 'warning' :
                        insight.severity === 'low' ? 'info' :
                        'success'
                      }>
                        {insight.severity}
                      </Badge>
                      <span className="text-xs text-gray-500">{insight.category}</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{insight.description}</p>
                    <div className="bg-gray-50 border border-gray-200 p-2 rounded">
                      <div className="text-xs text-gray-900"><strong>Recommendation:</strong> {insight.recommendation}</div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <div className="text-center py-6 text-gray-500">
              <div className="text-3xl mb-2">📋</div>
              <div>No insights available yet</div>
            </div>
          </Card>
        )}
      </div>

      {/* Recovery Plan (Read-only) */}
      {details?.plan && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-3">💪 Recovery Plan</h3>
          <Card>
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-lg font-semibold text-gray-800">{details.plan.name}</h4>
                <span className="text-sm text-gray-600">Week {details.plan.currentWeek} of {details.plan.duration}</span>
              </div>
              <p className="text-sm text-gray-600 mb-2"><strong>Goal:</strong> {details.plan.goal}</p>
              <p className="text-xs text-gray-500">Created by {details.plan.createdBy} on {details.plan.startDate}</p>
            </div>

            {/* Exercises */}
            <div className="mb-4">
              <h5 className="font-medium text-gray-800 mb-2">Prescribed Exercises</h5>
              <div className="space-y-2">
                {details.plan.exercises.map((exercise, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div>
                      <span className="text-sm font-medium text-gray-800">{exercise.name}</span>
                      <span className="text-xs text-gray-500 ml-2">({exercise.category})</span>
                    </div>
                    <span className="text-xs text-gray-600">{exercise.frequency}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Restrictions */}
            {details.plan.restrictions && details.plan.restrictions.length > 0 && (
              <div className="mb-4">
                <h5 className="font-medium text-gray-800 mb-2 text-red-600">⚠️ Training Restrictions</h5>
                <ul className="space-y-1">
                  {details.plan.restrictions.map((restriction, index) => (
                    <li key={index} className="text-sm text-gray-700 flex items-start space-x-2">
                      <span className="text-red-500 mt-0.5">•</span>
                      <span>{restriction}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Physio Notes */}
            {details.plan.notes && (
              <div className="bg-yellow-50 p-3 rounded-lg">
                <div className="text-xs font-medium text-yellow-800 mb-1">Notes from Physiotherapist:</div>
                <div className="text-sm text-yellow-900">{details.plan.notes}</div>
              </div>
            )}
          </Card>
        </div>
      )}

      {/* Comments Section */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-3">💬 Coach Comments</h3>
        
        {/* Add New Comment */}
        <Card>
          <h5 className="font-medium text-gray-800 mb-2">Add Comment</h5>
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Add your observations, notes, or feedback about training sessions..."
            className="w-full h-24 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none mb-3"
          />
          <button
            onClick={handleSubmitComment}
            disabled={!newComment.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Add Comment
          </button>
        </Card>

        {/* Comment History */}
        {details?.comments && details.comments.length > 0 ? (
          <div className="space-y-3 mt-4">
            {details.comments.slice().reverse().map((comment) => (
              <Card key={comment.id}>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                    {comment.author.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-medium text-gray-800">{comment.author}</span>
                      <span className="text-xs text-gray-500">{comment.date}</span>
                    </div>
                    <p className="text-sm text-gray-700">{comment.text}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <div className="text-center py-4 text-gray-500">
              <div className="text-2xl mb-1">💬</div>
              <div className="text-sm">No comments yet. Be the first to add one!</div>
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}
