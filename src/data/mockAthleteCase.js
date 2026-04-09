// Mock Athlete Case Data - Easy to edit manually

export const athleteCase = {
  // Basic Athlete Information
  athlete: {
    id: 'ATH001',
    name: 'John Athlete',
    age: 24,
    sport: 'Football',
    position: 'Midfielder',
    height: '180 cm',
    weight: '75 kg',
    joinDate: '2024-01-15',
    avatar: 'JA'
  },

  // Baseline Data - Initial Assessment
  baseline: {
    // Video assessments
    videos: [
      {
        id: 'VID001',
        title: 'Running Gait Analysis',
        url: '/videos/gait-analysis.mp4',
        uploadDate: '2024-01-20',
        duration: '2:30',
        thumbnail: '/thumbnails/gait.jpg',
        notes: 'Initial baseline - slight pronation observed'
      },
      {
        id: 'VID002',
        title: 'Squat Assessment',
        url: '/videos/squat-test.mp4',
        uploadDate: '2024-01-20',
        duration: '1:45',
        thumbnail: '/thumbnails/squat.jpg',
        notes: 'Good form, minor knee valgus'
      },
      {
        id: 'VID003',
        title: 'Balance Test',
        url: '/videos/balance.mp4',
        uploadDate: '2024-01-21',
        duration: '3:10',
        thumbnail: '/thumbnails/balance.jpg',
        notes: 'Right leg weaker than left'
      }
    ],

    // Physical readings and measurements
    readings: {
      mobility: {
        ankleFlexion: { left: 35, right: 32, unit: 'degrees', status: 'normal' },
        hipFlexion: { left: 120, right: 118, unit: 'degrees', status: 'normal' },
        shoulderRotation: { left: 85, right: 88, unit: 'degrees', status: 'good' }
      },
      strength: {
        quadStrength: { left: 85, right: 82, unit: 'kg', status: 'good' },
        hamstringStrength: { left: 65, right: 63, unit: 'kg', status: 'moderate' },
        coreStrength: { rating: 7, unit: 'out of 10', status: 'good' }
      },
      cardiovascular: {
        restingHeartRate: 58,
        vo2Max: 52,
        recoveryRate: 'Good',
        lastTested: '2024-01-22'
      },
      pain: {
        rightKnee: { level: 2, description: 'Mild discomfort after training' },
        lowerBack: { level: 0, description: 'No pain' }
      }
    },

    assessmentDate: '2024-01-20',
    assessedBy: 'Dr. Sarah Smith'
  },

  // Insights from Analysis
  insights: [
    {
      id: 'INS001',
      category: 'Biomechanics',
      severity: 'moderate',
      title: 'Slight knee valgus during squatting',
      description: 'Right knee shows inward movement during deep squat. May increase ACL injury risk.',
      recommendation: 'Focus on hip strengthening and movement control',
      identifiedDate: '2024-01-20'
    },
    {
      id: 'INS002',
      category: 'Balance',
      severity: 'low',
      title: 'Right leg balance deficit',
      description: 'Single-leg balance test shows 15% weakness on right side compared to left.',
      recommendation: 'Include unilateral stability exercises',
      identifiedDate: '2024-01-21'
    },
    {
      id: 'INS003',
      category: 'Strength',
      severity: 'low',
      title: 'Hamstring-quad ratio slightly low',
      description: 'Hamstring to quadriceps strength ratio at 76% (ideal: 80%+)',
      recommendation: 'Prioritize hamstring strengthening',
      identifiedDate: '2024-01-22'
    },
    {
      id: 'INS004',
      category: 'Recovery',
      severity: 'good',
      title: 'Excellent cardiovascular fitness',
      description: 'VO2 max of 52 indicates strong aerobic capacity for position.',
      recommendation: 'Maintain current cardio routine',
      identifiedDate: '2024-01-22'
    }
  ],

  // Training/Recovery Plan
  plan: {
    name: 'Injury Prevention & Performance Plan',
    startDate: '2024-01-25',
    duration: '8 weeks',
    goal: 'Correct biomechanical imbalances and reduce injury risk',
    
    // Exercise program
    exercises: [
      {
        id: 'EX001',
        name: 'Single Leg Balance',
        category: 'Balance',
        sets: 3,
        reps: '30 seconds',
        frequency: 'Daily',
        difficulty: 'Easy',
        instructions: 'Stand on right leg, maintain balance for 30s. Progress to eyes closed.',
        videoUrl: '/exercises/single-leg-balance.mp4',
        targetArea: 'Right leg stability'
      },
      {
        id: 'EX002',
        name: 'Hip Bridges',
        category: 'Strength',
        sets: 3,
        reps: 12,
        frequency: '3x per week',
        difficulty: 'Moderate',
        instructions: 'Lie on back, feet flat, lift hips. Squeeze glutes at top.',
        videoUrl: '/exercises/hip-bridges.mp4',
        targetArea: 'Glutes, hamstrings'
      },
      {
        id: 'EX003',
        name: 'Nordic Hamstring Curls',
        category: 'Strength',
        sets: 3,
        reps: 8,
        frequency: '2x per week',
        difficulty: 'Hard',
        instructions: 'Kneeling position, controlled forward lean. Build up slowly.',
        videoUrl: '/exercises/nordic-curls.mp4',
        targetArea: 'Hamstrings'
      },
      {
        id: 'EX004',
        name: 'Monster Walks',
        category: 'Strength',
        sets: 3,
        reps: 15,
        frequency: '3x per week',
        difficulty: 'Easy',
        instructions: 'Resistance band around knees, walk sideways maintaining tension.',
        videoUrl: '/exercises/monster-walks.mp4',
        targetArea: 'Hip abductors'
      },
      {
        id: 'EX005',
        name: 'Box Squats',
        category: 'Strength',
        sets: 3,
        reps: 10,
        frequency: '2x per week',
        difficulty: 'Moderate',
        instructions: 'Squat to box, focus on knees tracking over toes.',
        videoUrl: '/exercises/box-squats.mp4',
        targetArea: 'Quads, glutes, form correction'
      },
      {
        id: 'EX006',
        name: 'Foam Rolling - IT Band',
        category: 'Recovery',
        sets: 1,
        reps: '2 minutes per side',
        frequency: 'Daily',
        difficulty: 'Easy',
        instructions: 'Slow, controlled rolling along outer thigh.',
        videoUrl: '/exercises/foam-rolling.mp4',
        targetArea: 'Mobility, recovery'
      }
    ],

    // Weekly schedule template
    weeklySchedule: {
      monday: ['EX001', 'EX002', 'EX004', 'EX006'],
      tuesday: ['EX001', 'EX006'],
      wednesday: ['EX001', 'EX002', 'EX003', 'EX005', 'EX006'],
      thursday: ['EX001', 'EX006'],
      friday: ['EX001', 'EX002', 'EX004', 'EX006'],
      saturday: ['EX001', 'EX003', 'EX005', 'EX006'],
      sunday: ['EX001', 'EX006']
    },

    createdBy: 'Dr. Sarah Smith',
    notes: 'Focus on right leg stability and hamstring strengthening. Monitor knee pain.'
  },

  // Progress Tracking
  progress: {
    // Weekly metrics
    weeklyMetrics: [
      {
        week: 1,
        date: '2024-01-25',
        compliance: 95, // percentage
        painLevel: 2,
        energyLevel: 7,
        completed: true,
        notes: 'Good start, slight fatigue'
      },
      {
        week: 2,
        date: '2024-02-01',
        compliance: 90,
        painLevel: 1,
        energyLevel: 8,
        completed: true,
        notes: 'Pain decreasing, feeling stronger'
      },
      {
        week: 3,
        date: '2024-02-08',
        compliance: 85,
        painLevel: 1,
        energyLevel: 7,
        completed: true,
        notes: 'Missed 2 sessions due to match schedule'
      },
      {
        week: 4,
        date: '2024-02-15',
        compliance: 100,
        painLevel: 0,
        energyLevel: 9,
        completed: true,
        notes: 'No pain! Balance improving significantly'
      },
      {
        week: 5,
        date: '2024-02-22',
        compliance: 0,
        painLevel: 0,
        energyLevel: 8,
        completed: false,
        notes: 'Current week in progress'
      }
    ],

    // Performance improvements
    improvements: {
      balanceTest: {
        baseline: 15, // seconds on right leg
        current: 28,
        target: 30,
        unit: 'seconds',
        improvement: '+87%'
      },
      hamstringStrength: {
        baseline: 63,
        current: 70,
        target: 75,
        unit: 'kg',
        improvement: '+11%'
      },
      painScore: {
        baseline: 2,
        current: 0,
        target: 0,
        unit: 'out of 10',
        improvement: '100% reduced'
      },
      squatForm: {
        baseline: 'Moderate valgus',
        current: 'Minimal valgus',
        target: 'No valgus',
        improvement: 'Significant'
      }
    },

    // Reassessment data
    lastReassessment: {
      date: '2024-02-15',
      performedBy: 'Dr. Sarah Smith',
      summary: 'Excellent progress. Balance greatly improved. Knee tracking better. Continue program.',
      nextReassessment: '2024-03-15'
    },

    overallProgress: 75 // percentage to completion
  },

  // Case Status
  status: 'active',
  lastUpdated: '2024-02-22'
}

// Export individual sections for easy access
export const { athlete, baseline, insights, plan, progress } = athleteCase

// Helper function to get exercises by day
export const getExercisesByDay = (day) => {
  const exerciseIds = athleteCase.plan.weeklySchedule[day.toLowerCase()] || []
  return exerciseIds.map(id => 
    athleteCase.plan.exercises.find(ex => ex.id === id)
  ).filter(Boolean)
}

// Helper function to get current week progress
export const getCurrentWeekProgress = () => {
  return athleteCase.progress.weeklyMetrics.find(week => !week.completed) || 
         athleteCase.progress.weeklyMetrics[athleteCase.progress.weeklyMetrics.length - 1]
}

// Helper function to get insights by severity
export const getInsightsBySeverity = (severity) => {
  return athleteCase.insights.filter(insight => insight.severity === severity)
}
