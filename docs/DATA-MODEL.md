# Moove Platform - Data Model

## 1. User & Role Structure

### Core Principle
- **One Athlete → One of Each Role** (1:1:1:1)
- **One Professional → Many Athletes** (1:N)

```
Athlete (1) ←→ (1) Physiotherapist
            ←→ (1) Coach
            ←→ (1) Caretaker
```

---

## 2. User Base Schema

### User (Account)
```javascript
{
  userId: "string (UUID)",
  email: "string (unique)",
  passwordHash: "string",
  roles: ["athlete" | "physiotherapist" | "coach" | "caretaker"],
  profile: {
    firstName: "string",
    lastName: "string",
    avatar: "string (URL or initials)",
    phone: "string (optional)",
    dateOfBirth: "date",
    gender: "string"
  },
  organizationId: "string (UUID)", // Optional - for multi-org setups
  status: "active" | "inactive" | "suspended",
  createdAt: "timestamp",
  updatedAt: "timestamp",
  lastLoginAt: "timestamp"
}
```

---

## 3. Role-Specific Profiles

### Athlete Profile
```javascript
{
  athleteId: "string (UUID)",
  userId: "string (UUID)", // Links to User
  sportInfo: {
    sport: "string",
    position: "string",
    team: "string (optional)",
    level: "professional" | "collegiate" | "amateur"
  },
  injuryInfo: {
    currentInjury: "string",
    injuryDate: "date",
    injuryType: "string",
    injurySeverity: "mild" | "moderate" | "severe",
    recoveryTimeline: "string"
  },
  assignedTeam: {
    physiotherapistId: "string (UUID)", // Required - 1:1 relationship
    coachId: "string (UUID)",           // Required - 1:1 relationship
    caretakerId: "string (UUID)"        // Required - 1:1 relationship
  },
  status: "active" | "recovering" | "cleared" | "inactive",
  createdAt: "timestamp",
  updatedAt: "timestamp"
}
```

### Physiotherapist Profile
```javascript
{
  physiotherapistId: "string (UUID)",
  userId: "string (UUID)", // Links to User
  credentials: {
    licenseNumber: "string",
    specializations: ["string", "string"],
    certifications: ["string"]
  },
  assignedAthletes: ["athleteId", "athleteId"], // Array of athlete IDs (1:N)
  maxCaseload: "number (default: 15)",
  availability: {
    schedule: "object",
    timezone: "string"
  },
  createdAt: "timestamp",
  updatedAt: "timestamp"
}
```

### Coach Profile
```javascript
{
  coachId: "string (UUID)",
  userId: "string (UUID)", // Links to User
  coachingInfo: {
    sport: "string",
    specialization: "string",
    yearsExperience: "number"
  },
  assignedAthletes: ["athleteId", "athleteId"], // Array of athlete IDs (1:N)
  maxAthletes: "number (default: 20)",
  createdAt: "timestamp",
  updatedAt: "timestamp"
}
```

### Caretaker Profile
```javascript
{
  caretakerId: "string (UUID)",
  userId: "string (UUID)", // Links to User
  caretakerInfo: {
    type: "nurse" | "assistant" | "trainer" | "family",
    certifications: ["string"]
  },
  assignedAthletes: ["athleteId", "athleteId"], // Array of athlete IDs (1:N)
  maxAthletes: "number (default: 10)",
  shiftSchedule: {
    shifts: ["object"],
    timezone: "string"
  },
  createdAt: "timestamp",
  updatedAt: "timestamp"
}
```

---

## 4. Relationship Table (Care Team)

### AthleteTeam (Junction/Bridge Table)
```javascript
{
  teamId: "string (UUID)",
  athleteId: "string (UUID)",       // One athlete
  physiotherapistId: "string (UUID)", // One physio
  coachId: "string (UUID)",         // One coach
  caretakerId: "string (UUID)",     // One caretaker
  assignedDate: "timestamp",
  status: "active" | "inactive",
  createdAt: "timestamp",
  updatedAt: "timestamp"
}
```

**Constraints:**
- One athlete can only have ONE active team at a time
- Each role can appear in MULTIPLE teams (multiple athletes)
- Unique constraint on (athleteId, status='active')

---

## 5. Access Control Rules

### Data Access Matrix

| Role            | Can Access                                                |
|-----------------|-----------------------------------------------------------|
| **Athlete**     | Own data only (assessments, plans, progress)              |
| **Physiotherapist** | All assigned athletes' data (read/write)              |
| **Coach**       | All assigned athletes' data (read-only for clinical, write for training) |
| **Caretaker**   | All assigned athletes' daily tasks and compliance (read/write) |

### Access Control Functions
```javascript
// Check if user can access athlete data
function canAccessAthlete(userId, athleteId, requestedRole) {
  // 1. Get user's role from User table
  // 2. If role is 'athlete', check if userId matches athleteId
  // 3. If role is professional, check AthleteTeam relationship
  // 4. Return boolean
}

// Get all athletes accessible by user
function getAccessibleAthletes(userId, userRole) {
  if (userRole === 'athlete') {
    return [athleteId] // Only themselves
  }
  if (userRole === 'physiotherapist') {
    return AthleteTeam.findAll({ physiotherapistId: userId })
  }
  if (userRole === 'coach') {
    return AthleteTeam.findAll({ coachId: userId })
  }
  if (userRole === 'caretaker') {
    return AthleteTeam.findAll({ caretakerId: userId })
  }
}
```

---

## 6. Database Indexes (for Performance)

```javascript
// User table
Index: { email: 1 } // Unique
Index: { userId: 1, roles: 1 }

// Athlete Profile
Index: { athleteId: 1 }
Index: { userId: 1 } // Unique
Index: { "assignedTeam.physiotherapistId": 1 }
Index: { "assignedTeam.coachId": 1 }
Index: { "assignedTeam.caretakerId": 1 }

// Professional Profiles
Index: { physiotherapistId: 1, assignedAthletes: 1 }
Index: { coachId: 1, assignedAthletes: 1 }
Index: { caretakerId: 1, assignedAthletes: 1 }

// AthleteTeam (Care Team)
Index: { athleteId: 1, status: 1 } // Unique for active
Index: { physiotherapistId: 1 }
Index: { coachId: 1 }
Index: { caretakerId: 1 }
```

---

## 7. Example Relationships

### Scenario: 3 Athletes, 2 Physios, 2 Coaches, 1 Caretaker

```
Athlete A ─┬→ Physiotherapist 1
           ├→ Coach 1
           └→ Caretaker 1

Athlete B ─┬→ Physiotherapist 1  (same physio)
           ├→ Coach 2
           └→ Caretaker 1        (same caretaker)

Athlete C ─┬→ Physiotherapist 2
           ├→ Coach 2            (same coach)
           └→ Caretaker 1        (same caretaker)
```

**Data Access:**
- Athlete A: Sees only their own data
- Physiotherapist 1: Sees Athletes A & B
- Physiotherapist 2: Sees Athlete C
- Coach 1: Sees Athlete A
- Coach 2: Sees Athletes B & C
- Caretaker 1: Sees all Athletes A, B, C

---

## 8. API Query Examples

### Get Athlete's Care Team
```javascript
GET /api/athletes/{athleteId}/team
// Returns: { physio: {...}, coach: {...}, caretaker: {...} }
```

### Get Physiotherapist's Athletes
```javascript
GET /api/physiotherapists/{physioId}/athletes
// Returns: [athlete1, athlete2, ...]
```

### Check Access Permission
```javascript
POST /api/access/check
Body: { userId, athleteId, action: "read" | "write" }
// Returns: { allowed: true/false, role: "..." }
```

---

## Next Steps

1. ✅ User & Role structure defined
2. ⏭️ Detailed clinical data models (assessments, exercises, plans)
3. ⏭️ Activity & audit log structure
4. ⏭️ Real-time notification system
5. ⏭️ File storage structure (videos, images)

Ready to define the detailed clinical data models?
