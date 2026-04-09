# Firestore Seed Data - Example Documents

This file contains example documents for each collection. Use these to populate your Firestore database for testing.

## How to Add Seed Data

### Option 1: Firebase Console (Manual)
1. Go to https://console.firebase.google.com/project/watch-mail-trial/firestore
2. Create collections manually
3. Add documents with IDs and data below

### Option 2: Admin SDK Script (Automated)
```javascript
const admin = require('firebase-admin');
const serviceAccount = require('./serviceAccountKey.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

// Run: node seed-data.js
```

---

## Task 2: Core Entities

### Collection: `organizations`
```javascript
db.collection('organizations').doc('org_001').set({
  id: 'org_001',
  name: 'Mumbai Sports Institute',
  type: 'INSTITUTE',
  isCofounder: true,
  createdAt: admin.firestore.Timestamp.now(),
  updatedAt: admin.firestore.Timestamp.now()
});

db.collection('organizations').doc('org_002').set({
  id: 'org_002',
  name: 'Chennai Cricket Club',
  type: 'CLUB',
  isCofounder: false,
  createdAt: admin.firestore.Timestamp.now(),
  updatedAt: admin.firestore.Timestamp.now()
});
```

### Collection: `users`
```javascript
// Senior Physiotherapist
db.collection('users').doc('user_sr_001').set({
  id: 'user_sr_001',
  email: 'dr.sharma@institute.com',
  fullName: 'Dr. Anita Sharma',
  role: 'SR_PHYSIO',
  orgId: 'org_001',
  phone: '+91-9876543210',
  dateOfBirth: '1985-03-15',
  avatar: 'https://i.pravatar.cc/150?img=1',
  status: 'active',
  createdAt: admin.firestore.Timestamp.now(),
  updatedAt: admin.firestore.Timestamp.now(),
  lastLoginAt: admin.firestore.Timestamp.now()
});

// Junior Physiotherapist
db.collection('users').doc('user_jr_001').set({
  id: 'user_jr_001',
  email: 'priya.patel@institute.com',
  fullName: 'Priya Patel',
  role: 'JR_PHYSIO',
  orgId: 'org_001',
  phone: '+91-9876543211',
  dateOfBirth: '1992-07-20',
  avatar: 'https://i.pravatar.cc/150?img=2',
  status: 'active',
  createdAt: admin.firestore.Timestamp.now(),
  updatedAt: admin.firestore.Timestamp.now(),
  lastLoginAt: admin.firestore.Timestamp.now()
});

// Intern
db.collection('users').doc('user_intern_001').set({
  id: 'user_intern_001',
  email: 'raj.intern@institute.com',
  fullName: 'Raj Kumar',
  role: 'INTERN',
  orgId: 'org_001',
  phone: '+91-9876543212',
  dateOfBirth: '2000-01-10',
  avatar: 'https://i.pravatar.cc/150?img=3',
  status: 'active',
  createdAt: admin.firestore.Timestamp.now(),
  updatedAt: admin.firestore.Timestamp.now(),
  lastLoginAt: admin.firestore.Timestamp.now()
});

// Athlete
db.collection('users').doc('user_athlete_001').set({
  id: 'user_athlete_001',
  email: 'virat.athlete@cricket.com',
  fullName: 'Virat Singh',
  role: 'ATHLETE',
  orgId: 'org_002',
  phone: '+91-9876543213',
  dateOfBirth: '1998-11-05',
  avatar: 'https://i.pravatar.cc/150?img=4',
  status: 'active',
  createdAt: admin.firestore.Timestamp.now(),
  updatedAt: admin.firestore.Timestamp.now(),
  lastLoginAt: admin.firestore.Timestamp.now()
});
```

### Collection: `athletes`
```javascript
db.collection('athletes').doc('athlete_001').set({
  id: 'athlete_001',
  userId: 'user_athlete_001',
  orgId: 'org_002',
  sport: 'Cricket',
  position: 'Fast Bowler',
  team: 'Chennai Super Kings',
  level: 'professional',
  currentInjury: 'Shoulder rotator cuff strain',
  injuryDate: '2026-02-15',
  injuryType: 'Soft tissue',
  injurySeverity: 'moderate',
  recoveryTimeline: '6-8 weeks',
  baselineMetrics: {
    vo2Max: 55.2,
    maxStrength: {
      bench: 80,
      squat: 120,
      deadlift: 140
    },
    flexibility: {
      shoulderROM: 175,
      hipROM: 120
    },
    baselineDate: '2026-01-10'
  },
  medicalHistory: {
    previousInjuries: [
      {
        date: '2024-11-20',
        injury: 'Hamstring strain',
        recovery: '4 weeks'
      }
    ],
    allergies: ['Ibuprofen'],
    chronicConditions: [],
    surgeries: []
  },
  status: 'recovering',
  createdAt: admin.firestore.Timestamp.now(),
  updatedAt: admin.firestore.Timestamp.now()
});
```

---

## Task 3: Gatekeeper Taxonomy

### Collection: `masterTaxonomy`
```javascript
// Verified diagnosis tags
db.collection('masterTaxonomy').doc('tag_001').set({
  tagId: 'tag_001',
  category: 'DIAGNOSIS',
  tagName: 'ACL Tear - Grade 2',
  isVerified: true,
  suggestedBy: 'user_jr_001',
  verifiedBy: 'user_sr_001',
  metadata: {
    description: 'Partial tear of anterior cruciate ligament',
    icd10Code: 'S83.511A'
  },
  createdAt: admin.firestore.Timestamp.now(),
  verifiedAt: admin.firestore.Timestamp.now()
});

db.collection('masterTaxonomy').doc('tag_002').set({
  tagId: 'tag_002',
  category: 'EXERCISE',
  tagName: 'Single Leg Squat',
  isVerified: true,
  suggestedBy: 'user_jr_001',
  verifiedBy: 'user_sr_001',
  metadata: {
    description: 'Unilateral lower body strengthening exercise'
  },
  createdAt: admin.firestore.Timestamp.now(),
  verifiedAt: admin.firestore.Timestamp.now()
});

db.collection('masterTaxonomy').doc('tag_003').set({
  tagId: 'tag_003',
  category: 'NUTRITION',
  tagName: 'High Protein - Recovery Phase',
  isVerified: true,
  suggestedBy: 'user_sr_001',
  verifiedBy: 'user_sr_001',
  metadata: {
    description: 'Increased protein intake for tissue repair'
  },
  createdAt: admin.firestore.Timestamp.now(),
  verifiedAt: admin.firestore.Timestamp.now()
});
```

### Collection: `tagSuggestions`
```javascript
db.collection('tagSuggestions').doc('sugg_001').set({
  suggestionId: 'sugg_001',
  category: 'EXERCISE',
  tagName: 'Eccentric Calf Raises',
  suggestedBy: 'user_intern_001',
  status: 'PENDING',
  reviewedBy: null,
  reviewNotes: null,
  reviewedAt: null,
  createdAt: admin.firestore.Timestamp.now()
});

db.collection('tagSuggestions').doc('sugg_002').set({
  suggestionId: 'sugg_002',
  category: 'EQUIPMENT',
  tagName: 'TheraBand - Heavy Resistance',
  suggestedBy: 'user_jr_001',
  status: 'APPROVED',
  reviewedBy: 'user_sr_001',
  reviewNotes: 'Good addition for strength training',
  reviewedAt: admin.firestore.Timestamp.now(),
  createdAt: admin.firestore.Timestamp.now()
});
```

---

## Task 4: Assessments & Async Workflow

### Collection: `assessments`
```javascript
db.collection('assessments').doc('assess_001').set({
  assessmentId: 'assess_001',
  athleteId: 'athlete_001',
  internId: 'user_intern_001',
  rawVideoGcsUri: 'gs://moove-videos/raw/assess_001.mp4',
  processedVideoGcsUri: 'gs://moove-videos/processed/assess_001.mp4',
  videoUrl: 'https://storage.googleapis.com/moove-videos/assess_001.mp4',
  thumbnailUrl: 'https://storage.googleapis.com/moove-videos/thumbs/assess_001.jpg',
  status: 'READY_L1',
  uploadedAt: admin.firestore.Timestamp.now(),
  aiProcessingStartedAt: admin.firestore.Timestamp.now(),
  aiProcessingCompletedAt: admin.firestore.Timestamp.now(),
  publishedAt: null,
  assessmentType: 'video',
  exerciseType: 'Squat',
  aiAnalysis: {
    confidence: 0.89,
    keypoints: [],
    metrics: {
      squatDepth: 85,
      kneeAlignment: 92,
      hipMobility: 78
    }
  },
  statusPulse: {
    currentStatus: 'READY_L1',
    progress: 50,
    message: 'Ready for Level 1 review',
    estimatedCompletion: admin.firestore.Timestamp.fromDate(new Date(Date.now() + 24*60*60*1000)),
    lastUpdated: admin.firestore.Timestamp.now()
  },
  createdAt: admin.firestore.Timestamp.now(),
  updatedAt: admin.firestore.Timestamp.now()
});

// Workflow config subcollection
db.collection('assessments').doc('assess_001')
  .collection('workflowConfig').doc('config').set({
    isLevel2Enabled: false,
    isPanelMode: false,
    priority: 'MEDIUM',
    estimatedCompletionTime: admin.firestore.Timestamp.fromDate(new Date(Date.now() + 24*60*60*1000)),
    assignedReviewers: ['user_jr_001'],
    createdAt: admin.firestore.Timestamp.now(),
    updatedAt: admin.firestore.Timestamp.now()
  });
```

---

## Task 5: Movement Data

### Collection: `movementData`
```javascript
db.collection('movementData').doc('move_001').set({
  movementId: 'move_001',
  assessmentId: 'assess_001',
  frameCoordinates: {
    frame_0: {
      timestamp: 0.0,
      keypoints: {
        nose: {x: 0.5, y: 0.3, z: 0.1, visibility: 0.99},
        left_shoulder: {x: 0.4, y: 0.5, z: 0.2, visibility: 0.98}
        // ... more keypoints
      }
    }
  },
  summaryMetrics: {
    exerciseType: 'squat',
    repetitions: 10,
    jointAngles: {
      kneeFlexion: {min: 45, max: 165, avg: 105},
      hipFlexion: {min: 30, max: 120, avg: 75}
    },
    rangeOfMotion: {
      left_knee: 120,
      right_knee: 118
    },
    symmetry: {
      left_right: 0.98
    }
  },
  movementEmbedding: new Array(768).fill(0).map(() => Math.random()),
  createdAt: admin.firestore.Timestamp.now()
});
```

---

## Task 6: Reviews & Prescriptions

### Collection: `reviews`
```javascript
db.collection('reviews').doc('review_001').set({
  reviewId: 'review_001',
  assessmentId: 'assess_001',
  reviewerId: 'user_jr_001',
  reviewLevel: 1,
  findingsTags: ['tag_001', 'tag_002'],
  timestampedNotes: {
    '00:15': 'Poor knee alignment - valgus collapse',
    '00:32': 'Good depth achieved',
    '01:05': 'Compensatory hip shift to left'
  },
  overallFindings: 'Athlete shows good squat depth but demonstrates knee valgus...',
  recommendations: [
    'Focus on knee tracking exercises',
    'Strengthen hip abductors'
  ],
  createdAt: admin.firestore.Timestamp.now()
});
```

### Collection: `prescriptions`
```javascript
db.collection('prescriptions').doc('rx_001').set({
  prescriptionId: 'rx_001',
  assessmentId: 'assess_001',
  athleteId: 'athlete_001',
  finalizedBySrPhysio: 'user_sr_001',
  status: 'PUBLISHED',
  movementPlan: {
    phase: 'strengthening',
    duration: '4 weeks',
    exercises: [
      {
        exerciseId: 'ex_001',
        name: 'Wall Squats',
        sets: 3,
        reps: 12,
        frequency: 'daily'
      }
    ]
  },
  nutritionPlan: {
    protein_g_per_kg: 1.8,
    caloric_surplus: 300,
    supplements: ['Omega-3', 'Vitamin D']
  },
  equipmentSpecs: {
    required: [
      {
        item: 'Resistance Band',
        specification: 'Medium resistance (15-25 lbs)'
      }
    ]
  },
  coachConstraints: 'No jumping drills for 2 weeks',
  draftedBy: 'user_jr_001',
  approvalHistory: [
    {
      approvedBy: 'user_sr_001',
      timestamp: admin.firestore.Timestamp.now(),
      notes: 'Approved'
    }
  ],
  createdAt: admin.firestore.Timestamp.now(),
  publishedAt: admin.firestore.Timestamp.now(),
  updatedAt: admin.firestore.Timestamp.now()
});
```

---

## Task 7: Daily Tracking

### Collection: `dailyLogs`
```javascript
db.collection('dailyLogs').doc('log_20260325_athlete_001').set({
  logId: 'log_20260325_athlete_001',
  athleteId: 'athlete_001',
  date: '2026-03-25',
  readinessScore: 7,
  fatigue: 4,
  sleep: {
    hours: 7.5,
    quality: 'good'
  },
  sorenessMap: {
    knee: 3,
    shoulder: 1,
    lower_back: 0,
    hamstring: 2
  },
  netPerformance: 3,
  athleteNotes: 'Feeling better today',
  createdAt: admin.firestore.Timestamp.now(),
  updatedAt: admin.firestore.Timestamp.now()
});
```

### Collection: `complianceTracking`
```javascript
db.collection('complianceTracking').doc('comp_001').set({
  complianceId: 'comp_001',
  prescriptionId: 'rx_001',
  athleteId: 'athlete_001',
  date: '2026-03-25',
  completionPercentage: 85,
  exercisesCompleted: 5,
  exercisesTotal: 6,
  exerciseDetails: [
    {
      exerciseId: 'ex_001',
      completed: true,
      sets_completed: 3,
      sets_prescribed: 3
    }
  ],
  internNotes: 'Good progress',
  createdAt: admin.firestore.Timestamp.now()
});
```

---

## Deploy Instructions

1. **Install Functions Dependencies:**
   ```bash
   cd functions
   npm install
   cd ..
   ```

2. **Deploy everything:**
   ```bash
   firebase deploy
   ```

3. **Or deploy individually:**
   ```bash
   firebase deploy --only firestore    # Rules + Indexes
   firebase deploy --only storage      # Storage rules
   firebase deploy --only functions    # Cloud Functions
   firebase deploy --only hosting      # Frontend
   ```

4. **Test Cloud Functions locally:**
   ```bash
   firebase emulators:start
   ```

5. **Add seed data via console:**
   - https://console.firebase.google.com/project/watch-mail-trial/firestore
   - Copy-paste documents from above

Done! All 7 tasks (2-8) implemented in Firestore. 🎉
