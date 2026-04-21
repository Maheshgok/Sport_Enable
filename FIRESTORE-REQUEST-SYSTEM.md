# Firestore Request System Schema

## Overview
Allows physiotherapists to request new exercises and baseline measurements that require admin approval before being added to the system.

## Collections

### 1. `exerciseRequests/`
Requests from physiotherapists to add new exercises to the exercise library.

```javascript
{
  requestId: "auto-generated-id",
  requestedBy: "user-id",  // Physiotherapist user ID
  requestedByName: "Dr. Sarah Chen",
  requestedByEmail: "sarah@example.com",
  
  // Exercise details
  exerciseName: "Single Leg Romanian Deadlift",
  description: "Advanced balance and posterior chain exercise",
  category: "strength",  // strength, flexibility, mobility, balance, cardio
  difficultyLevel: "advanced",  // beginner, intermediate, advanced
  
  targetMuscles: ["hamstrings", "glutes", "core"],
  targetJoints: ["hip", "knee", "ankle"],
  injuryTypes: ["ACL recovery", "hamstring strain", "ankle instability"],
  
  // Instructions
  instructions: "Detailed step-by-step instructions...",
  precautions: "Avoid if balance is severely compromised...",
  
  // Metadata
  durationMinutes: 10,
  equipmentNeeded: ["dumbbell", "balance pad"],
  
  // Media (optional - can be added later)
  videoUrl: "",
  thumbnailUrl: "",
  instructionImages: [],
  
  // Justification
  reason: "Many ACL patients need this progression but it's not in library",
  useCase: "Post-ACL rehab, weeks 8-12",
  
  // Status tracking
  status: "pending",  // pending, approved, rejected
  reviewedBy: null,  // Admin user ID
  reviewedAt: null,
  reviewNotes: "",
  approvedExerciseId: null,  // Reference to exercise_library if approved
  
  // Timestamps
  createdAt: Timestamp,
  updatedAt: Timestamp
}
```

**Indexes:**
- `requestedBy` (for physio to see their requests)
- `status` (for admin to see pending)
- `createdAt` (for sorting)

---

### 2. `baselineRequests/`
Requests from physiotherapists to add new baseline measurement types for specific sports/conditions.

```javascript
{
  requestId: "auto-generated-id",
  requestedBy: "user-id",  // Physiotherapist user ID
  requestedByName: "Dr. Sarah Chen",
  requestedByEmail: "sarah@example.com",
  
  // Baseline details
  measurementName: "Single Leg Hop Distance",
  measurementType: "functional",  // functional, strength, mobility, endurance
  unit: "cm",
  
  // Sport/condition context
  sportId: 1,  // Football
  sportName: "Football",
  applicableConditions: ["ACL recovery", "ankle sprain"],
  
  // Reference values
  normalRange: {
    min: 90,
    max: 110,
    description: "Percentage of uninvolved leg distance"
  },
  
  // Testing protocol
  testingProtocol: "Patient hops on one leg for maximum distance...",
  equipmentNeeded: ["measuring tape", "non-slip surface"],
  
  // Justification
  reason: "Critical metric for return-to-sport decisions in football",
  researchReferences: ["Smith et al. 2025 AJSM", "Jones 2024 BJSM"],
  
  // Status tracking
  status: "pending",  // pending, approved, rejected
  reviewedBy: null,
  reviewedAt: null,
  reviewNotes: "",
  
  // Timestamps
  createdAt: Timestamp,
  updatedAt: Timestamp
}
```

**Indexes:**
- `requestedBy`
- `status`
- `sportId`
- `createdAt`

---

### 3. `requestNotifications/`
Notifications for request status changes.

```javascript
{
  notificationId: "auto-generated-id",
  userId: "user-id",  // Recipient
  type: "request_approved",  // request_approved, request_rejected, new_request_pending
  
  // Request reference
  requestType: "exercise",  // exercise, baseline
  requestId: "request-doc-id",
  requestTitle: "Single Leg Romanian Deadlift",
  
  // Message
  message: "Your exercise request has been approved",
  
  // Status
  read: false,
  
  // Timestamps
  createdAt: Timestamp
}
```

---

## Permission Matrix

| Action | Physiotherapist | Coach | Athlete | Parent | Admin |
|--------|----------------|-------|---------|---------|-------|
| Submit exercise request | ✅ | ❌ | ❌ | ❌ | ✅ |
| Submit baseline request | ✅ | ❌ | ❌ | ❌ | ✅ |
| View own requests | ✅ | ❌ | ❌ | ❌ | ✅ |
| View all pending requests | ❌ | ❌ | ❌ | ❌ | ✅ |
| Approve/reject requests | ❌ | ❌ | ❌ | ❌ | ✅ |
| Add notes to requests | ✅ (own) | ❌ | ❌ | ❌ | ✅ |

---

## API Endpoints

### Physiotherapist Endpoints

#### Submit Exercise Request
```
POST /api/physio/request-exercise
Auth: Required (physiotherapist or admin)

Body:
{
  exerciseName: string,
  description: string,
  category: string,
  difficultyLevel: string,
  targetMuscles: string[],
  targetJoints: string[],
  injuryTypes: string[],
  instructions: string,
  precautions: string,
  durationMinutes: number,
  equipmentNeeded: string[],
  reason: string,
  useCase: string
}

Response: { requestId, status: "pending" }
```

#### Submit Baseline Request
```
POST /api/physio/request-baseline
Auth: Required (physiotherapist or admin)

Body:
{
  measurementName: string,
  measurementType: string,
  unit: string,
  sportId: number,
  sportName: string,
  applicableConditions: string[],
  normalRange: { min, max, description },
  testingProtocol: string,
  equipmentNeeded: string[],
  reason: string,
  researchReferences: string[]
}

Response: { requestId, status: "pending" }
```

#### Get My Requests
```
GET /api/physio/my-requests?type=all|exercise|baseline
Auth: Required (physiotherapist or admin)

Response: { requests: [...] }
```

### Admin Endpoints

#### Get Pending Requests
```
GET /api/admin/requests/pending?type=all|exercise|baseline
Auth: Required (admin)

Response: { requests: [...] }
```

#### Get All Requests
```
GET /api/admin/requests?status=all|pending|approved|rejected
Auth: Required (admin)

Response: { requests: [...] }
```

#### Approve Exercise Request
```
POST /api/admin/requests/exercise/:requestId/approve
Auth: Required (admin)

Body:
{
  reviewNotes: string (optional),
  addToLibrary: boolean  // If true, creates exercise in library
}

Response: { success, exerciseId }
```

#### Reject Request
```
POST /api/admin/requests/:requestId/reject
Auth: Required (admin)

Body:
{
  reviewNotes: string (required)
}

Response: { success }
```

---

## Workflow

### Exercise Request Flow
1. **Physiotherapist** submits request via UI form
2. System creates document in `exerciseRequests/` with status "pending"
3. System creates notification for admins in `requestNotifications/`
4. **Admin** reviews request in admin dashboard
5. **Admin** approves/rejects:
   - **If approved**: Exercise added to library (future: Firestore or database)
   - **If rejected**: Status updated, reason provided
6. System creates notification for physiotherapist
7. Physiotherapist sees status update in "My Requests" page

### Baseline Request Flow
Similar to exercise request, but creates baseline measurement configuration instead of library entry.

---

## Future Enhancements
1. **Duplicate Detection**: Check if similar exercise/baseline already exists
2. **Collaborative Editing**: Multiple physios can upvote requests
3. **Comments**: Discussion thread on requests
4. **Media Upload**: Allow physios to upload demo videos
5. **Auto-approval**: Trusted physios get auto-approved after X successful requests
6. **Analytics**: Track most requested exercises/baselines by sport

---

## Cost Estimation (Firestore)

**Assumption**: 10 active physiotherapists, 5 requests/month each

- Writes: 50 requests/month = 50 writes
- Reads: Each physio checks 2x/month = 100 reads, Admin checks 10x/month = 500 reads
- Storage: ~50KB per request × 600 requests/year = 30MB

**Monthly Cost**: ~$0.50/month (negligible)
