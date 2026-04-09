// Mock data for coach - athletes under their supervision

export const coachAthletes = [
  {
    id: 'ATH001',
    name: 'John Athlete',
    age: 24,
    sport: 'Football',
    position: 'Midfielder',
    avatar: 'JA',
    status: 'active', // active, recovering, cleared
    condition: 'Knee rehabilitation - progressing well',
    recoveryProgress: 75,
    physio: 'Dr. Sarah Smith',
    lastUpdate: '2024-02-22',
    trainingStatus: 'Modified training',
    nextSession: 'Today 6PM'
  },
  {
    id: 'ATH002',
    name: 'Sarah Runner',
    age: 28,
    sport: 'Athletics',
    position: '800m',
    avatar: 'SR',
    status: 'recovering',
    condition: 'Ankle sprain - early recovery phase',
    recoveryProgress: 30,
    physio: 'Dr. Sarah Smith',
    lastUpdate: '2024-02-20',
    trainingStatus: 'Rest',
    nextSession: 'Pending clearance'
  },
  {
    id: 'ATH003',
    name: 'Mike Strong',
    age: 22,
    sport: 'Weightlifting',
    position: 'Heavyweight',
    avatar: 'MS',
    status: 'active',
    condition: 'Lower back strain - maintenance phase',
    recoveryProgress: 60,
    physio: 'Dr. Sarah Smith',
    lastUpdate: '2024-02-21',
    trainingStatus: 'Modified training',
    nextSession: 'Tomorrow 9AM'
  },
  {
    id: 'ATH004',
    name: 'Emma Swift',
    age: 26,
    sport: 'Swimming',
    position: 'Freestyle',
    avatar: 'ES',
    status: 'cleared',
    condition: 'Shoulder rehabilitation - completed',
    recoveryProgress: 100,
    physio: 'Dr. Sarah Smith',
    lastUpdate: '2024-02-10',
    trainingStatus: 'Full training',
    nextSession: 'Today 3PM'
  },
  {
    id: 'ATH005',
    name: 'David Jump',
    age: 23,
    sport: 'Basketball',
    position: 'Power Forward',
    avatar: 'DJ',
    status: 'recovering',
    condition: 'Awaiting initial assessment',
    recoveryProgress: 10,
    physio: 'Dr. Sarah Smith',
    lastUpdate: '2024-02-23',
    trainingStatus: 'Rest',
    nextSession: 'Assessment scheduled'
  },
  {
    id: 'ATH006',
    name: 'Lisa Fast',
    age: 25,
    sport: 'Track & Field',
    position: 'Sprinter',
    avatar: 'LF',
    status: 'active',
    condition: 'Hamstring strengthening program',
    recoveryProgress: 85,
    physio: 'Dr. Sarah Smith',
    lastUpdate: '2024-02-23',
    trainingStatus: 'Full training',
    nextSession: 'Today 5PM'
  }
]

// Athlete details including insights and plans (read-only for coach)
export const athleteDetails = {
  ATH001: {
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
        category: 'Recovery',
        severity: 'good',
        title: 'Excellent cardiovascular fitness',
        description: 'VO2 max of 52 indicates strong aerobic capacity for position.',
        recommendation: 'Maintain current cardio routine',
        identifiedDate: '2024-01-22'
      }
    ],
    plan: {
      name: 'Injury Prevention & Performance Plan',
      duration: '8 weeks',
      goal: 'Correct biomechanical imbalances and reduce injury risk',
      startDate: '2024-01-25',
      currentWeek: 5,
      exercises: [
        { name: 'Single Leg Balance', frequency: 'Daily', category: 'Balance' },
        { name: 'Hip Bridges', frequency: '3x per week', category: 'Strength' },
        { name: 'Nordic Hamstring Curls', frequency: '2x per week', category: 'Strength' },
        { name: 'Monster Walks', frequency: '3x per week', category: 'Strength' },
        { name: 'Box Squats', frequency: '2x per week', category: 'Strength' },
        { name: 'Foam Rolling - IT Band', frequency: 'Daily', category: 'Recovery' }
      ],
      restrictions: [
        'No high-impact jumping for 2 more weeks',
        'Avoid deep squats with heavy load',
        'Monitor knee pain during lateral movements'
      ],
      createdBy: 'Dr. Sarah Smith',
      notes: 'Focus on right leg stability and hamstring strengthening. Monitor knee pain.'
    },
    comments: [
      {
        id: 'COM001',
        author: 'Mike Coach',
        date: '2024-02-20',
        text: 'Great progress on balance exercises. Ready to increase sprint intensity gradually.'
      },
      {
        id: 'COM002',
        author: 'Mike Coach',
        date: '2024-02-15',
        text: 'Athlete reports feeling more confident during cutting movements. Will monitor closely during team practice.'
      }
    ]
  },
  ATH002: {
    insights: [
      {
        id: 'INS004',
        category: 'Mobility',
        severity: 'moderate',
        title: 'Limited ankle dorsiflexion',
        description: 'Right ankle shows 30% less range of motion compared to left.',
        recommendation: 'Continue mobility work and gradual loading',
        identifiedDate: '2024-02-15'
      }
    ],
    plan: {
      name: 'Ankle Sprain Recovery Protocol',
      duration: '6 weeks',
      goal: 'Restore full ankle mobility and strength',
      startDate: '2024-02-15',
      currentWeek: 2,
      exercises: [
        { name: 'Ankle Circles', frequency: 'Daily', category: 'Mobility' },
        { name: 'Calf Raises', frequency: '3x per week', category: 'Strength' },
        { name: 'Balance Board Work', frequency: 'Daily', category: 'Balance' }
      ],
      restrictions: [
        'No running until week 4',
        'No jumping activities',
        'Use ankle brace during all activities'
      ],
      createdBy: 'Dr. Sarah Smith',
      notes: 'Progress slowly. Pain should not exceed 3/10 during exercises.'
    },
    comments: []
  },
  ATH003: {
    insights: [
      {
        id: 'INS005',
        category: 'Strength',
        severity: 'moderate',
        title: 'Weak core stability',
        description: 'Core strength rated 5/10. Contributing to lower back compensation.',
        recommendation: 'Prioritize core strengthening before heavy lifting',
        identifiedDate: '2024-02-01'
      }
    ],
    plan: {
      name: 'Lower Back Rehabilitation',
      duration: '6 weeks',
      goal: 'Improve core strength and restore pain-free movement',
      startDate: '2024-02-01',
      currentWeek: 4,
      exercises: [
        { name: 'Plank Hold', frequency: 'Daily', category: 'Strength' },
        { name: 'Hip Bridges', frequency: '3x per week', category: 'Strength' },
        { name: 'Dead Bug', frequency: 'Daily', category: 'Core' },
        { name: 'Cat-Cow Stretch', frequency: 'Daily', category: 'Mobility' }
      ],
      restrictions: [
        'No deadlifts over 60% 1RM until cleared',
        'Avoid spinal flexion under load',
        'Stop if pain exceeds 2/10'
      ],
      createdBy: 'Dr. Sarah Smith',
      notes: 'Focus on movement quality over load. Core activation critical.'
    },
    comments: [
      {
        id: 'COM003',
        author: 'Mike Coach',
        date: '2024-02-18',
        text: 'Deadlift form looking much better. Continuing with lighter weights as prescribed.'
      }
    ]
  },
  ATH004: {
    insights: [
      {
        id: 'INS006',
        category: 'Recovery',
        severity: 'good',
        title: 'Full shoulder mobility restored',
        description: 'All ROM tests within normal range. Strength at 95% of baseline.',
        recommendation: 'Gradual return to full training load',
        identifiedDate: '2024-02-10'
      }
    ],
    plan: {
      name: 'Return to Performance Program',
      duration: '4 weeks',
      goal: 'Safe return to competitive swimming',
      startDate: '2024-02-10',
      currentWeek: 2,
      exercises: [
        { name: 'Shoulder Mobility Routine', frequency: 'Daily', category: 'Mobility' },
        { name: 'Rotator Cuff Strengthening', frequency: '3x per week', category: 'Strength' },
        { name: 'Swimming Drills (technique focus)', frequency: '4x per week', category: 'Sport-Specific' }
      ],
      restrictions: [
        'Gradually increase yardage by 10% per week',
        'Avoid maximum effort sprints for 2 more weeks'
      ],
      createdBy: 'Dr. Sarah Smith',
      notes: 'Cleared for full training. Monitor for any pain recurrence.'
    },
    comments: [
      {
        id: 'COM004',
        author: 'Mike Coach',
        date: '2024-02-22',
        text: 'Excellent progress! Stroke mechanics back to pre-injury form. Planning competition return next month.'
      },
      {
        id: 'COM005',
        author: 'Mike Coach',
        date: '2024-02-12',
        text: 'First full practice session completed without issues. Very encouraging.'
      }
    ]
  }
}
