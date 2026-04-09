// Mock data for physiotherapist - multiple athlete cases

export const athleteCases = [
  {
    id: 'CASE001',
    athlete: {
      id: 'ATH001',
      name: 'John Athlete',
      age: 24,
      sport: 'Football',
      avatar: 'JA'
    },
    status: 'active', // active, assessment, completed
    condition: 'Knee instability',
    assignedDate: '2024-01-20',
    lastUpdate: '2024-02-22',
    priority: 'normal', // low, normal, high
    progress: 75
  },
  {
    id: 'CASE002',
    athlete: {
      id: 'ATH002',
      name: 'Sarah Runner',
      age: 28,
      sport: 'Athletics',
      avatar: 'SR'
    },
    status: 'assessment',
    condition: 'Ankle sprain recovery',
    assignedDate: '2024-02-15',
    lastUpdate: '2024-02-20',
    priority: 'high',
    progress: 30
  },
  {
    id: 'CASE003',
    athlete: {
      id: 'ATH003',
      name: 'Mike Strong',
      age: 22,
      sport: 'Weightlifting',
      avatar: 'MS'
    },
    status: 'active',
    condition: 'Lower back strain',
    assignedDate: '2024-02-01',
    lastUpdate: '2024-02-21',
    priority: 'normal',
    progress: 60
  },
  {
    id: 'CASE004',
    athlete: {
      id: 'ATH004',
      name: 'Emma Swift',
      age: 26,
      sport: 'Swimming',
      avatar: 'ES'
    },
    status: 'completed',
    condition: 'Shoulder rehabilitation',
    assignedDate: '2024-01-05',
    lastUpdate: '2024-02-10',
    priority: 'low',
    progress: 100
  },
  {
    id: 'CASE005',
    athlete: {
      id: 'ATH005',
      name: 'David Jump',
      age: 23,
      sport: 'Basketball',
      avatar: 'DJ'
    },
    status: 'assessment',
    condition: 'Awaiting initial assessment',
    assignedDate: '2024-02-23',
    lastUpdate: '2024-02-23',
    priority: 'high',
    progress: 10
  }
]

// Available exercises for assignment
export const exerciseLibrary = [
  {
    id: 'EX001',
    name: 'Single Leg Balance',
    category: 'Balance',
    difficulty: 'Easy',
    targetAreas: ['Stability', 'Proprioception']
  },
  {
    id: 'EX002',
    name: 'Hip Bridges',
    category: 'Strength',
    difficulty: 'Moderate',
    targetAreas: ['Glutes', 'Hamstrings']
  },
  {
    id: 'EX003',
    name: 'Nordic Hamstring Curls',
    category: 'Strength',
    difficulty: 'Hard',
    targetAreas: ['Hamstrings']
  },
  {
    id: 'EX004',
    name: 'Monster Walks',
    category: 'Strength',
    difficulty: 'Easy',
    targetAreas: ['Hip Abductors']
  },
  {
    id: 'EX005',
    name: 'Box Squats',
    category: 'Strength',
    difficulty: 'Moderate',
    targetAreas: ['Quads', 'Glutes']
  },
  {
    id: 'EX006',
    name: 'Foam Rolling - IT Band',
    category: 'Recovery',
    difficulty: 'Easy',
    targetAreas: ['Mobility', 'Recovery']
  },
  {
    id: 'EX007',
    name: 'Calf Raises',
    category: 'Strength',
    difficulty: 'Easy',
    targetAreas: ['Calves', 'Ankle Stability']
  },
  {
    id: 'EX008',
    name: 'Plank Hold',
    category: 'Strength',
    difficulty: 'Moderate',
    targetAreas: ['Core', 'Stability']
  },
  {
    id: 'EX009',
    name: 'Wall Slides',
    category: 'Mobility',
    difficulty: 'Easy',
    targetAreas: ['Shoulders', 'Posture']
  },
  {
    id: 'EX010',
    name: 'Lateral Lunges',
    category: 'Strength',
    difficulty: 'Moderate',
    targetAreas: ['Hips', 'Adductors']
  }
]

// Mock assessment videos and readings for cases
export const caseAssessments = {
  CASE001: {
    videos: [
      {
        id: 'VID001',
        title: 'Running Gait Analysis',
        uploadDate: '2024-01-20',
        duration: '2:30',
        status: 'analyzed'
      },
      {
        id: 'VID002',
        title: 'Squat Assessment',
        uploadDate: '2024-01-20',
        duration: '1:45',
        status: 'analyzed'
      }
    ],
    readings: {
      mobility: {
        ankleFlexion: { left: 35, right: 32, unit: 'degrees', status: 'normal' },
        hipFlexion: { left: 120, right: 118, unit: 'degrees', status: 'normal' }
      },
      strength: {
        quadStrength: { left: 85, right: 82, unit: 'kg', status: 'good' },
        hamstringStrength: { left: 65, right: 63, unit: 'kg', status: 'moderate' }
      },
      pain: {
        rightKnee: { level: 2, description: 'Mild discomfort after training' }
      }
    },
    diagnosis: 'Slight knee valgus during squatting. Right knee shows inward movement. Focus on hip strengthening and movement control.',
    assignedExercises: ['EX001', 'EX002', 'EX004', 'EX005']
  },
  CASE002: {
    videos: [
      {
        id: 'VID003',
        title: 'Ankle ROM Test',
        uploadDate: '2024-02-15',
        duration: '1:15',
        status: 'pending'
      }
    ],
    readings: {
      mobility: {
        ankleFlexion: { left: 28, right: 40, unit: 'degrees', status: 'limited' }
      },
      pain: {
        rightAnkle: { level: 3, description: 'Moderate pain with dorsiflexion' }
      }
    },
    diagnosis: '',
    assignedExercises: []
  },
  CASE003: {
    videos: [
      {
        id: 'VID004',
        title: 'Deadlift Form Check',
        uploadDate: '2024-02-01',
        duration: '2:00',
        status: 'analyzed'
      }
    ],
    readings: {
      mobility: {
        hipFlexion: { left: 105, right: 102, unit: 'degrees', status: 'limited' }
      },
      strength: {
        coreStrength: { rating: 5, unit: 'out of 10', status: 'weak' }
      },
      pain: {
        lowerBack: { level: 4, description: 'Pain during extension' }
      }
    },
    diagnosis: 'Limited hip mobility causing compensatory lower back movement. Weak core stability.',
    assignedExercises: ['EX002', 'EX006', 'EX008']
  }
}
