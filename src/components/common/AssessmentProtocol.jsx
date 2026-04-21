import { useState } from 'react'
import Card from './Card'

export default function AssessmentProtocol() {
  const [currentStep, setCurrentStep] = useState(0)

  // Hardcoded protocol data
  const protocol = {
    name: 'Baseline Movement Assessment',
    description: 'Complete these movements to establish your baseline mobility and strength patterns',
    movements: [
      {
        id: 'M001',
        name: 'Squat Test',
        description: 'Assess lower body mobility and strength',
        duration: '30 seconds',
        reps: '5 repetitions',
        instructions: [
          'Stand with feet shoulder-width apart',
          'Lower down slowly as if sitting in a chair',
          'Keep chest up and core engaged',
          'Ensure knees track over toes (no inward collapse)',
          'Lower until thighs are parallel to ground',
          'Push through heels to return to starting position',
          'Maintain controlled tempo throughout'
        ],
        cameraAngle: 'Side view - full body visible',
        tips: [
          'Keep your weight on your heels',
          'Don\'t let knees extend past toes',
          'Breathe steadily throughout'
        ]
      },
      {
        id: 'M002',
        name: 'Single Leg Balance',
        description: 'Test balance and stability on each leg',
        duration: '60 seconds total',
        reps: '30 seconds per leg',
        instructions: [
          'Stand tall with good posture',
          'Lift right leg, bending knee to 90 degrees',
          'Hold steady position for 30 seconds',
          'Keep standing leg slightly bent',
          'Use arms for balance if needed',
          'Switch to left leg and repeat',
          'Focus eyes on fixed point ahead'
        ],
        cameraAngle: 'Front view - full body visible',
        tips: [
          'Start near a wall for safety',
          'Focus on a spot to help balance',
          'Engage your core muscles'
        ]
      },
      {
        id: 'M003',
        name: 'Shoulder Mobility Test',
        description: 'Evaluate shoulder range of motion',
        duration: '45 seconds',
        reps: '5 repetitions each direction',
        instructions: [
          'Stand with feet hip-width apart',
          'Extend arms straight out to sides at shoulder height',
          'Make large circles forward for 5 repetitions',
          'Reverse direction for 5 circles backward',
          'Keep movements smooth and controlled',
          'Gradually increase circle size',
          'Maintain upright posture throughout'
        ],
        cameraAngle: 'Side or front view - upper body focus',
        tips: [
          'Don\'t force the movement',
          'Keep shoulders relaxed',
          'Breathe naturally'
        ]
      },
      {
        id: 'M004',
        name: 'Plank Hold',
        description: 'Assess core strength and stability',
        duration: '30-60 seconds',
        reps: '1 sustained hold',
        instructions: [
          'Start in push-up position',
          'Lower onto forearms, elbows under shoulders',
          'Keep body in straight line from head to heels',
          'Engage core muscles',
          'Don\'t let hips sag or pike up',
          'Hold position for maximum time (up to 60 seconds)',
          'Breathe steadily throughout'
        ],
        cameraAngle: 'Side view - full body visible',
        tips: [
          'Squeeze glutes to protect lower back',
          'Look down to maintain neutral neck',
          'Stop if form breaks down'
        ]
      }
    ]
  }

  const totalSteps = protocol.movements.length
  const currentMovement = protocol.movements[currentStep]
  const isFirstStep = currentStep === 0
  const isLastStep = currentStep === totalSteps - 1

  const handleNext = () => {
    if (!isLastStep) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (!isFirstStep) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleFinish = () => {
    alert('Assessment complete! In production, this would submit your assessment results.')
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Protocol Header */}
      <div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">{protocol.name}</h2>
        <p className="text-gray-600">{protocol.description}</p>
      </div>

      {/* Progress Indicator */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <div className="text-sm text-gray-500">
            Movement {currentStep + 1} of {totalSteps}
          </div>
          <div className="text-sm font-medium text-gray-900">
            {Math.round(((currentStep + 1) / totalSteps) * 100)}% Complete
          </div>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-gray-900 h-2 rounded-full"
            style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
          />
        </div>
        
        {/* Step Dots */}
        <div className="flex justify-center space-x-2 mt-4">
          {protocol.movements.map((_, index) => (
            <div
              key={index}
              className={`w-2 h-2 rounded-full ${
                index === currentStep
                  ? 'bg-gray-900 w-8'
                  : index < currentStep
                  ? 'bg-gray-400'
                  : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
      </Card>

      {/* Current Movement */}
      <Card>
        <div className="space-y-6">
          {/* Movement Header */}
          <div className="border-b border-gray-200 pb-4">
            <div className="flex items-start justify-between mb-2">
              <h3 className="text-xl font-semibold text-gray-900">{currentMovement.name}</h3>
              <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-md text-sm">
                {currentMovement.duration}
              </span>
            </div>
            <p className="text-gray-600 mb-3">{currentMovement.description}</p>
            <div className="flex items-center space-x-6 text-sm text-gray-500">
              <div className="flex items-center space-x-2">
                <span>📹</span>
                <span>{currentMovement.cameraAngle}</span>
              </div>
              <div className="flex items-center space-x-2">
                <span>🔄</span>
                <span>{currentMovement.reps}</span>
              </div>
            </div>
          </div>

          {/* Reference Video Placeholder */}
          <div className="bg-gray-900 rounded-lg aspect-video flex items-center justify-center">
            <div className="text-center">
              <div className="text-5xl mb-3">🎥</div>
              <div className="text-white text-base font-medium mb-2">Reference Video</div>
              <div className="text-gray-400 text-sm mb-4">{currentMovement.name} - Demonstration</div>
              <button className="px-5 py-2 bg-white text-gray-900 rounded-md hover:bg-gray-100 font-medium">
                ▶ Play Video
              </button>
            </div>
          </div>

          {/* Instructions */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3 text-base">
              Step-by-Step Instructions
            </h4>
            <ol className="space-y-3">
              {currentMovement.instructions.map((instruction, index) => (
                <li key={index} className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-medium">
                    {index + 1}
                  </span>
                  <span className="text-gray-700 pt-0.5">{instruction}</span>
                </li>
              ))}
            </ol>
          </div>

          {/* Tips */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">
              Tips
            </h4>
            <ul className="space-y-1">
              {currentMovement.tips.map((tip, index) => (
                <li key={index} className="text-gray-700 text-sm flex items-start">
                  <span className="mr-2">•</span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Upload Section */}
          <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <div className="text-3xl mb-3">📤</div>
            <h4 className="font-medium text-gray-900 mb-2">Upload Your Movement</h4>
            <p className="text-gray-600 text-sm mb-4">
              Upload a video of yourself performing this movement
            </p>
            <label className="cursor-pointer px-6 py-3 bg-gray-900 text-white rounded-md hover:bg-gray-800 font-medium inline-block">
              Upload Video
              <input type="file" accept="video/*" className="hidden" />
            </label>
            <div className="mt-3 text-xs text-gray-500">
              Or drag and drop video file here
            </div>
          </div>
        </div>
      </Card>

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between">
        <button
          onClick={handlePrevious}
          disabled={isFirstStep}
          className={`px-5 py-2 rounded-md font-medium ${
            isFirstStep
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-white border border-gray-300 text-gray-700 hover:border-gray-900'
          }`}
        >
          Previous
        </button>

        <div className="text-sm text-gray-500">
          Step {currentStep + 1} of {totalSteps}
        </div>

        {!isLastStep ? (
          <button
            onClick={handleNext}
            className="px-5 py-2 bg-gray-900 text-white rounded-md hover:bg-gray-800 font-medium"
          >
            Next
          </button>
        ) : (
          <button
            onClick={handleFinish}
            className="px-5 py-2 bg-gray-900 text-white rounded-md hover:bg-gray-800 font-medium"
          >
            Complete Assessment
          </button>
        )}
      </div>
    </div>
  )
}
