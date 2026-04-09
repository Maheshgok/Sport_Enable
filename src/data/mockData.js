// Mock data for the MVP - no backend needed

export const mockUser = {
  athlete: {
    name: 'John Athlete',
    email: 'john@example.com',
    avatar: 'JA'
  },
  physiotherapist: {
    name: 'Dr. Sarah Smith',
    email: 'sarah@example.com',
    avatar: 'SS'
  },
  coach: {
    name: 'Mike Coach',
    email: 'mike@example.com',
    avatar: 'MC'
  },
  caretaker: {
    name: 'Emma Care',
    email: 'emma@example.com',
    avatar: 'EC'
  }
}

export const mockStats = {
  athlete: [
    { label: 'Workouts This Week', value: '5' },
    { label: 'Total Hours', value: '12.5' },
    { label: 'Recovery Score', value: '85%' },
    { label: 'Next Session', value: 'Today 6PM' }
  ],
  physiotherapist: [
    { label: 'Active Patients', value: '12' },
    { label: 'Appointments Today', value: '5' },
    { label: 'Pending Reports', value: '3' },
    { label: 'Recovery Rate', value: '92%' }
  ],
  coach: [
    { label: 'Active Athletes', value: '18' },
    { label: 'Training Plans', value: '8' },
    { label: 'Sessions This Week', value: '24' },
    { label: 'Team Performance', value: '88%' }
  ],
  caretaker: [
    { label: 'Assigned Athletes', value: '6' },
    { label: 'Tasks Today', value: '8' },
    { label: 'Meals Planned', value: '18' },
    { label: 'Messages', value: '5' }
  ]
}

export const mockActivities = {
  athlete: [
    { id: 1, title: 'Morning Run', time: '6:00 AM', status: 'Completed' },
    { id: 2, title: 'Strength Training', time: '4:00 PM', status: 'Scheduled' },
    { id: 3, title: 'Recovery Session', time: '7:00 PM', status: 'Scheduled' }
  ],
  physiotherapist: [
    { id: 1, patient: 'John Doe', time: '9:00 AM', type: 'Initial Assessment' },
    { id: 2, patient: 'Jane Smith', time: '11:00 AM', type: 'Follow-up' },
    { id: 3, patient: 'Mike Johnson', time: '2:00 PM', type: 'Treatment' }
  ],
  coach: [
    { id: 1, athlete: 'John Athlete', plan: 'Endurance Training', progress: '75%' },
    { id: 2, athlete: 'Sarah Runner', plan: 'Speed Work', progress: '60%' },
    { id: 3, athlete: 'Mike Strong', plan: 'Strength Focus', progress: '85%' }
  ],
  caretaker: [
    { id: 1, task: 'Prepare breakfast', athlete: 'John Athlete', time: '7:00 AM' },
    { id: 2, task: 'Laundry pickup', athlete: 'Sarah Runner', time: '10:00 AM' },
    { id: 3, task: 'Meal prep', athlete: 'Mike Strong', time: '5:00 PM' }
  ]
}
