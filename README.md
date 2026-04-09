# Moove MVP - Multi-Role Dashboard

A minimal React frontend MVP for a multi-role dashboard system with no backend, authentication, or database integration.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

Visit `http://localhost:5173` to see the app.

## 📁 Folder Structure

```
moove/
├── public/                   # Static assets
├── src/
│   ├── components/          # Reusable React components
│   │   ├── layout/         # Layout components (Topbar, Sidebar, MainLayout)
│   │   │   ├── MainLayout.jsx    # Main app layout wrapper
│   │   │   ├── Topbar.jsx        # Top navigation bar with user info
│   │   │   └── Sidebar.jsx       # Role-specific sidebar navigation
│   │   └── common/         # Shared UI components
│   │       └── Card.jsx          # Reusable card component
│   │
│   ├── pages/              # Role-specific dashboard pages
│   │   ├── athlete/
│   │   │   └── AthleteDashboard.jsx
│   │   ├── physiotherapist/
│   │   │   └── PhysiotherapistDashboard.jsx
│   │   ├── coach/
│   │   │   └── CoachDashboard.jsx
│   │   └── caretaker/
│   │       └── CaretakerDashboard.jsx
│   │
│   ├── data/               # Mock data for the MVP
│   │   ├── mockData.js           # User info, stats, activities
│   │   └── mockAthleteCase.js    # Complete athlete case data structure
│   │
│   ├── App.jsx             # Main app component with role switching
│   ├── main.jsx            # React entry point
│   └── index.css           # Global styles with Tailwind
│
├── index.html              # HTML template
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
└── postcss.config.js       # PostCSS configuration
```

## 🗂️ Why This Structure?

### `/components`
- **Purpose**: Houses all reusable React components
- **layout/**: Components that define the app structure (Topbar, Sidebar, MainLayout)
- **common/**: Shared UI elements used across multiple pages (Card, Button, etc.)
- **Why**: Keeps UI components modular and reusable

### `/pages`
- **Purpose**: Role-specific dashboard views
- Each role gets its own folder (athlete, physiotherapist, coach, caretaker)
- **Why**: Separates concerns by user role while keeping code organized and scalable

### `/data`
- **Purpose**: Mock data that simulates backend responses
- Contains user profiles, stats, activities, etc.
- **Why**: Allows frontend development without backend dependency

#### Athlete Case Data Structure (`mockAthleteCase.js`)
Complete mock data for an athlete case including:
- **athlete**: Basic info (name, age, sport, position, physical stats)
- **baseline**: Initial assessment data
  - Videos: Gait analysis, squat tests, balance tests
  - Readings: Mobility, strength, cardiovascular, pain levels
- **insights**: AI/analysis findings with severity levels and recommendations
- **plan**: Training/recovery program
  - Exercises with sets, reps, frequency, instructions
  - Weekly schedule template
- **progress**: Tracking metrics
  - Weekly compliance, pain levels, energy levels
  - Performance improvements (before/after comparisons)

**Helper functions included:**
- `getExercisesByDay(day)` - Get exercises for specific day
- `getCurrentWeekProgress()` - Get current week metrics
- `getInsightsBySeverity(severity)` - Filter insights by severity level

### Root Files
- **App.jsx**: Main component with role switching logic
- **main.jsx**: React DOM entry point
- **index.css**: Global styles and Tailwind imports

## 🎨 Features

### Current Implementation
✅ Multi-role system (Athlete, Physiotherapist, Coach, Caretaker)  
✅ Clean layout with Topbar, Sidebar, and Main content area  
✅ Role-specific dashboards with mock data  
✅ Complete athlete case data structure (baseline, insights, plan, progress)  
✅ Basic state management with React hooks  
✅ Tailwind CSS for styling  
✅ Responsive design  
✅ Modular component structure  

### MVP Notes
- **No routing**: Simple role switcher in the topbar (easy to add React Router later)
- **No backend**: All data is mocked in `mockData.js`
- **No authentication**: Role selection is via dropdown (ready for auth integration)
- **No state management library**: Just useState (can add Context API or Redux when needed)

## 🔧 Technology Stack

- **React 18** - UI library
- **Vite** - Build tool (fast, modern)
- **Tailwind CSS** - Utility-first CSS framework
- **Functional Components** - Modern React patterns
- **React Hooks** - useState for simple state management

## 🎯 Role-Specific Features

### Athlete
- Workout tracking
- Progress monitoring
- Schedule view
- Recovery metrics

### Physiotherapist
- Patient management
- Appointment scheduling
- Treatment reports
- Recovery tracking

### Coach
- Athlete oversight
- Training plan management
- Performance analytics
- Team coordination

### Caretaker
- Daily task management
- Athlete care coordination
- Meal planning
- Communication hub

## 🚀 Next Steps (When Needed)

1. **Add Routing**: Install React Router for proper navigation
2. **Backend Integration**: Connect to API endpoints
3. **Authentication**: Add login/logout functionality
4. **State Management**: Add Context API or Redux if state grows complex
5. **More Components**: Build out specific features per role
6. **Testing**: Add unit and integration tests

## � Using Mock Athlete Case Data

The athlete case data structure is ready to use in your components:

```javascript
// Import the full case or specific sections
import { athleteCase, athlete, baseline, insights, plan, progress } from './data/mockAthleteCase'

// Or use helper functions
import { getExercisesByDay, getCurrentWeekProgress } from './data/mockAthleteCase'

// Example: Get Monday's exercises
const mondayExercises = getExercisesByDay('monday')

// Example: Get current week metrics
const currentWeek = getCurrentWeekProgress()
```

**View the example component**: `src/pages/athlete/AthleteCaseView.jsx` shows how to display all athlete case data with tabs.

**Easy to edit**: Open `mockAthleteCase.js` and modify values directly - no backend needed!

## 📝 Development Guidelines


- Keep components small and focused
- Use functional components and hooks
- Mock data lives in `/data` folder
- Each role gets its own page folder
- Shared components go in `/components/common`
- Layout components stay in `/components/layout`

---

**Built as a minimal MVP** - Easy to extend, modify, and scale when backend is ready! 🎉
