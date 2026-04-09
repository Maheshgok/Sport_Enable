// Mock data for caretaker - daily tasks and monitoring

export const assignedAthletes = [
  {
    id: 'ATH001',
    name: 'John Athlete',
    avatar: 'JA',
    sport: 'Football',
    status: 'active',
    compliance: 95
  },
  {
    id: 'ATH002',
    name: 'Sarah Runner',
    avatar: 'SR',
    sport: 'Athletics',
    status: 'recovering',
    compliance: 85
  },
  {
    id: 'ATH003',
    name: 'Mike Strong',
    avatar: 'MS',
    sport: 'Weightlifting',
    status: 'active',
    compliance: 90
  }
]

// Daily plan for each athlete
export const dailyPlans = {
  ATH001: {
    athleteName: 'John Athlete',
    date: new Date().toISOString().split('T')[0],
    tasks: [
      {
        id: 'TASK001',
        time: '07:00',
        type: 'Exercise',
        title: 'Single Leg Balance',
        description: '3 sets × 30 seconds each leg',
        priority: 'high',
        completed: false
      },
      {
        id: 'TASK002',
        time: '07:15',
        type: 'Meal',
        title: 'Morning Supplement',
        description: 'Protein shake + vitamins',
        priority: 'normal',
        completed: false
      },
      {
        id: 'TASK003',
        time: '09:00',
        type: 'Exercise',
        title: 'Foam Rolling - IT Band',
        description: '2 minutes per side',
        priority: 'normal',
        completed: false
      },
      {
        id: 'TASK004',
        time: '12:30',
        type: 'Meal',
        title: 'Lunch Preparation',
        description: 'High protein meal, low sodium',
        priority: 'high',
        completed: false
      },
      {
        id: 'TASK005',
        time: '16:00',
        type: 'Exercise',
        title: 'Hip Bridges',
        description: '3 sets × 12 reps',
        priority: 'high',
        completed: false
      },
      {
        id: 'TASK006',
        time: '16:15',
        type: 'Exercise',
        title: 'Monster Walks',
        description: '3 sets × 15 reps',
        priority: 'normal',
        completed: false
      },
      {
        id: 'TASK007',
        time: '18:00',
        type: 'Meal',
        title: 'Pre-Training Snack',
        description: 'Banana + energy bar',
        priority: 'normal',
        completed: false
      },
      {
        id: 'TASK008',
        time: '20:00',
        type: 'Care',
        title: 'Ice Knee (Right)',
        description: '15 minutes with ice pack',
        priority: 'high',
        completed: false
      },
      {
        id: 'TASK009',
        time: '21:00',
        type: 'Meal',
        title: 'Evening Recovery Meal',
        description: 'Lean protein + vegetables',
        priority: 'high',
        completed: false
      }
    ]
  },
  ATH002: {
    athleteName: 'Sarah Runner',
    date: new Date().toISOString().split('T')[0],
    tasks: [
      {
        id: 'TASK101',
        time: '07:00',
        type: 'Exercise',
        title: 'Ankle Circles',
        description: '3 sets × 10 each direction',
        priority: 'high',
        completed: false
      },
      {
        id: 'TASK102',
        time: '07:30',
        type: 'Meal',
        title: 'Breakfast',
        description: 'Oatmeal + fruit',
        priority: 'normal',
        completed: false
      },
      {
        id: 'TASK103',
        time: '10:00',
        type: 'Care',
        title: 'Ankle Brace Check',
        description: 'Ensure proper fit and support',
        priority: 'high',
        completed: false
      },
      {
        id: 'TASK104',
        time: '14:00',
        type: 'Exercise',
        title: 'Calf Raises',
        description: '3 sets × 12 reps',
        priority: 'high',
        completed: false
      },
      {
        id: 'TASK105',
        time: '19:00',
        type: 'Care',
        title: 'Ice Ankle',
        description: '20 minutes elevation + ice',
        priority: 'high',
        completed: false
      }
    ]
  },
  ATH003: {
    athleteName: 'Mike Strong',
    date: new Date().toISOString().split('T')[0],
    tasks: [
      {
        id: 'TASK201',
        time: '06:30',
        type: 'Exercise',
        title: 'Morning Stretching',
        description: 'Cat-cow stretch, 10 reps',
        priority: 'high',
        completed: false
      },
      {
        id: 'TASK202',
        time: '08:00',
        type: 'Meal',
        title: 'High Protein Breakfast',
        description: 'Eggs + whole grain toast',
        priority: 'normal',
        completed: false
      },
      {
        id: 'TASK203',
        time: '11:00',
        type: 'Exercise',
        title: 'Plank Hold',
        description: '3 sets × 45 seconds',
        priority: 'high',
        completed: false
      },
      {
        id: 'TASK204',
        time: '15:00',
        type: 'Exercise',
        title: 'Hip Bridges',
        description: '3 sets × 12 reps',
        priority: 'normal',
        completed: false
      },
      {
        id: 'TASK205',
        time: '20:00',
        type: 'Care',
        title: 'Heat Therapy - Lower Back',
        description: '15 minutes with heating pad',
        priority: 'normal',
        completed: false
      }
    ]
  }
}

// Monitoring alerts
export const alerts = {
  ATH001: [
    {
      id: 'ALT001',
      type: 'info',
      priority: 'normal',
      message: 'Compliance excellent this week (95%)',
      time: '2 hours ago'
    },
    {
      id: 'ALT002',
      type: 'reminder',
      priority: 'normal',
      message: 'Ice therapy scheduled for 8:00 PM',
      time: '30 minutes ago'
    }
  ],
  ATH002: [
    {
      id: 'ALT101',
      type: 'warning',
      priority: 'high',
      message: 'Athlete reported ankle pain level increased to 4/10',
      time: '1 hour ago'
    },
    {
      id: 'ALT102',
      type: 'reminder',
      priority: 'high',
      message: 'Ensure ankle brace is worn during all activities',
      time: '3 hours ago'
    },
    {
      id: 'ALT103',
      type: 'info',
      priority: 'normal',
      message: 'Physio appointment tomorrow at 10:00 AM',
      time: '5 hours ago'
    }
  ],
  ATH003: [
    {
      id: 'ALT201',
      type: 'success',
      priority: 'normal',
      message: 'Pain level reduced to 1/10 this week',
      time: '4 hours ago'
    },
    {
      id: 'ALT202',
      type: 'info',
      priority: 'normal',
      message: 'Compliance at 90% - good progress',
      time: '1 day ago'
    }
  ]
}

// Weekly compliance data
export const weeklyCompliance = {
  ATH001: [
    { day: 'Mon', compliance: 100 },
    { day: 'Tue', compliance: 95 },
    { day: 'Wed', compliance: 100 },
    { day: 'Thu', compliance: 90 },
    { day: 'Fri', compliance: 95 },
    { day: 'Sat', compliance: 100 },
    { day: 'Sun', compliance: 85 }
  ],
  ATH002: [
    { day: 'Mon', compliance: 80 },
    { day: 'Tue', compliance: 85 },
    { day: 'Wed', compliance: 90 },
    { day: 'Thu', compliance: 85 },
    { day: 'Fri', compliance: 85 },
    { day: 'Sat', compliance: 90 },
    { day: 'Sun', compliance: 80 }
  ],
  ATH003: [
    { day: 'Mon', compliance: 90 },
    { day: 'Tue', compliance: 95 },
    { day: 'Wed', compliance: 85 },
    { day: 'Thu', compliance: 90 },
    { day: 'Fri', compliance: 90 },
    { day: 'Sat', compliance: 95 },
    { day: 'Sun', compliance: 85 }
  ]
}
