# Mock Athlete Case Data - Quick Reference

## Overview

The `mockAthleteCase.js` file contains a complete athlete case data structure that simulates a real-world athlete assessment, treatment plan, and progress tracking system.

## Data Structure

### 1. Athlete Info
```javascript
athleteCase.athlete
```
- Basic profile information
- Sport and position
- Physical measurements
- Join date

### 2. Baseline Data
```javascript
athleteCase.baseline
```

#### Videos
Array of assessment videos with:
- Title and duration
- Upload date
- Notes from assessment

#### Readings
Structured measurements:
- **Mobility**: Ankle, hip, shoulder range of motion
- **Strength**: Quad, hamstring, core measurements
- **Cardiovascular**: Heart rate, VO2 max
- **Pain**: Current pain levels by area

### 3. Insights
```javascript
athleteCase.insights
```

Array of findings from analysis:
- Severity level (good/low/moderate/high)
- Category (biomechanics, balance, strength, etc.)
- Description and recommendation
- Identified date

### 4. Plan
```javascript
athleteCase.plan
```

#### Plan Details
- Name and goal
- Duration and dates
- Created by

#### Exercises
Array of exercises with:
- Sets, reps, frequency
- Difficulty level
- Instructions
- Target area
- Video URL (mock)

#### Weekly Schedule
Object mapping days to exercise IDs:
```javascript
plan.weeklySchedule.monday // ['EX001', 'EX002', ...]
```

### 5. Progress
```javascript
athleteCase.progress
```

#### Weekly Metrics
Array tracking each week:
- Compliance percentage
- Pain and energy levels
- Notes
- Completion status

#### Improvements
Before/after comparisons:
- Balance test results
- Strength measurements
- Pain reduction
- Form improvements

#### Reassessment
- Last assessment date
- Summary and next steps

## Helper Functions

### getExercisesByDay(day)
Returns array of exercise objects for a specific day.

```javascript
const mondayWorkout = getExercisesByDay('monday')
// Returns: [{ name: 'Single Leg Balance', ... }, ...]
```

### getCurrentWeekProgress()
Returns the current week's metrics or the most recent if all completed.

```javascript
const thisWeek = getCurrentWeekProgress()
// Returns: { week: 5, compliance: 100, painLevel: 0, ... }
```

### getInsightsBySeverity(severity)
Filters insights by severity level.

```javascript
const criticalIssues = getInsightsBySeverity('moderate')
```

## Usage Examples

### Display Athlete Profile
```javascript
import { athlete } from './data/mockAthleteCase'

function AthleteProfile() {
  return (
    <div>
      <h1>{athlete.name}</h1>
      <p>{athlete.sport} - {athlete.position}</p>
      <p>Age: {athlete.age} | Height: {athlete.height}</p>
    </div>
  )
}
```

### Show Exercise Plan
```javascript
import { plan, getExercisesByDay } from './data/mockAthleteCase'

function TodaysPlan() {
  const exercises = getExercisesByDay('monday')
  
  return (
    <div>
      <h2>{plan.name}</h2>
      {exercises.map(ex => (
        <div key={ex.id}>
          <h3>{ex.name}</h3>
          <p>{ex.sets} sets × {ex.reps}</p>
          <p>{ex.instructions}</p>
        </div>
      ))}
    </div>
  )
}
```

### Track Progress
```javascript
import { progress } from './data/mockAthleteCase'

function ProgressChart() {
  return (
    <div>
      <h2>Weekly Progress</h2>
      {progress.weeklyMetrics.map(week => (
        <div key={week.week}>
          <p>Week {week.week}: {week.compliance}% compliance</p>
          <p>Pain: {week.painLevel}/10</p>
        </div>
      ))}
    </div>
  )
}
```

### Display Improvements
```javascript
import { progress } from './data/mockAthleteCase'

function Improvements() {
  return (
    <div>
      {Object.entries(progress.improvements).map(([key, value]) => (
        <div key={key}>
          <h3>{key}</h3>
          <p>Before: {value.baseline} {value.unit}</p>
          <p>Now: {value.current} {value.unit}</p>
          <p className="success">{value.improvement}</p>
        </div>
      ))}
    </div>
  )
}
```

## Editing the Mock Data

All data is plain JavaScript - just open `mockAthleteCase.js` and edit:

### Add a New Exercise
```javascript
{
  id: 'EX007',
  name: 'Your Exercise',
  category: 'Strength',
  sets: 3,
  reps: 10,
  frequency: '3x per week',
  difficulty: 'Moderate',
  instructions: 'Step by step...',
  videoUrl: '/exercises/your-exercise.mp4',
  targetArea: 'Target muscles'
}
```

### Add a New Week of Progress
```javascript
{
  week: 6,
  date: '2024-03-01',
  compliance: 95,
  painLevel: 0,
  energyLevel: 9,
  completed: false,
  notes: 'Strong week!'
}
```

### Add a New Insight
```javascript
{
  id: 'INS005',
  category: 'Recovery',
  severity: 'good',
  title: 'Sleep quality improved',
  description: 'Better sleep patterns observed',
  recommendation: 'Maintain current sleep schedule',
  identifiedDate: '2024-03-01'
}
```

## Complete Example Component

See `src/pages/athlete/AthleteCaseView.jsx` for a full implementation showing:
- Tabbed navigation (Overview, Baseline, Insights, Plan, Progress)
- All data sections rendered
- Interactive UI with progress bars and metrics
- Helper function usage

## Benefits of This Structure

✅ **No backend needed** - Full data available immediately  
✅ **Easy to modify** - Plain JavaScript objects  
✅ **Realistic** - Mirrors real-world case structure  
✅ **Type-safe ready** - Can add TypeScript later  
✅ **Scalable** - Add more athletes by copying structure  

## Next Steps

When ready for backend:
1. Replace import from `mockAthleteCase.js` with API calls
2. Keep the same data structure in API responses
3. Components work without changes!

---

**The mock data is your friend** - Use it to build and test the entire UI before touching any backend! 🎉
