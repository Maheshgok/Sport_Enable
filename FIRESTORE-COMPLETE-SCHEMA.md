# Complete Firestore Schema for Moove Platform
## Adapted from PostgreSQL Tasks 2-8 for Firebase

---

## Collection Structure Overview

```
firestore/
├── organizations/
├── users/
├── athletes/
├── masterTaxonomy/
├── tagSuggestions/
├── assessments/
│   └── {assessmentId}/
│       ├── workflowConfig (subcollection)
│       └── statusPulses (real-time updates)
├── movementData/
├── reviews/
├── prescriptions/
├── dailyLogs/
├── complianceTracking/
└── analyticsCache/ (for computed views)
```

---

## Task 2: Core Entities (Users, Orgs, Athletes)

### Collection: `organizations`
```javascript
{
  "organizations/{orgId}": {
    "id": "org_001",
    "name": "Mumbai Sports Institute",
    "type": "INSTITUTE", // INSTITUTE | CLUB
    "isCofounder": true,
    "createdAt": Timestamp,
    "updatedAt": Timestamp
  }
}
```

### Collection: `users`
```javascript
{
  "users/{userId}": {
    "id": "user_001",
    "email": "dr.sharma@institute.com",
    "fullName": "Dr. Anita Sharma",
    "role": "SR_PHYSIO", // ADMIN | SR_PHYSIO | JR_PHYSIO | COACH | INTERN | ATHLETE
    "orgId": "org_001",
    
    // Additional profile fields
    "phone": "+91-9876543210",
    "dateOfBirth": "1985-03-15",
    "avatar": "https://storage.googleapis.com/...",
    
    // Account status
    "status": "active", // active | inactive | suspended
    "createdAt": Timestamp,
    "updatedAt": Timestamp,
    "lastLoginAt": Timestamp
  }
}
```

### Collection: `athletes`
```javascript
{
  "athletes/{athleteId}": {
    "id": "athlete_001",
    "userId": "user_001", // Reference to users collection
    "orgId": "org_001",
    
    // Sport info
    "sport": "Cricket",
    "position": "Fast Bowler",
    "team": "Mumbai Indians",
    "level": "professional",
    
    // Medical info
    "currentInjury": "Shoulder rotator cuff strain",
    "injuryDate": "2026-02-15",
    "injuryType": "Soft tissue",
    "injurySeverity": "moderate",
    "recoveryTimeline": "6-8 weeks",
    
    // NEW: Baseline metrics (JSONB → nested object)
    "baselineMetrics": {
      "vo2Max": 55.2,
      "maxStrength": {
        "bench": 80,
        "squat": 120,
        "deadlift": 140
      },
      "flexibility": {
        "shoulderROM": 175,
        "hipROM": 120
      },
      "baseline_date": "2026-01-10"
    },
    
    // NEW: Medical history (JSONB → nested object)
    "medicalHistory": {
      "previousInjuries": [
        {
          "date": "2024-11-20",
          "injury": "Hamstring strain",
          "recovery": "4 weeks"
        }
      ],
      "allergies": ["Ibuprofen"],
      "chronicConditions": [],
      "surgeries": []
    },
    
    "status": "recovering",
    "createdAt": Timestamp,
    "updatedAt": Timestamp
  }
}
```

**Indexes needed:**
- `orgId` (for filtering by organization)
- `userId` (for user-to-athlete lookup)
- `status` (for active athletes)

---

## Task 3: The 'Gatekeeper' Taxonomy (Master Tags)

### Collection: `masterTaxonomy`
```javascript
{
  "masterTaxonomy/{tagId}": {
    "tagId": "tag_001",
    "category": "DIAGNOSIS", // DIAGNOSIS | EXERCISE | NUTRITION | EQUIPMENT
    "tagName": "ACL Tear - Grade 2",
    "isVerified": true,
    "suggestedBy": "user_123", // User ID who suggested
    "verifiedBy": "user_456", // SR_PHYSIO who verified
    "metadata": {
      "description": "Partial tear of anterior cruciate ligament",
      "icd10Code": "S83.511A"
    },
    "createdAt": Timestamp,
    "verifiedAt": Timestamp
  }
}
```

### Collection: `tagSuggestions`
```javascript
{
  "tagSuggestions/{suggestionId}": {
    "suggestionId": "sugg_001",
    "category": "EXERCISE",
    "tagName": "Eccentric Calf Raises",
    "suggestedBy": "user_789", // JR_PHYSIO or INTERN
    "status": "PENDING", // PENDING | APPROVED | REJECTED
    
    // Review info (populated when reviewed)
    "reviewedBy": null, // SR_PHYSIO user ID
    "reviewNotes": null,
    "reviewedAt": null,
    
    "createdAt": Timestamp
  }
}
```

**Indexes needed:**
- `category` + `isVerified` (for verified tags by category)
- `status` + `createdAt` (for pending suggestions queue)

**Security Rule (Gatekeeper):**
```javascript
// Only SR_PHYSIO can approve/reject
allow update: if request.auth != null 
  && get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'SR_PHYSIO';
```

---

## Task 4: Assessments & Async Workflow States

### Collection: `assessments`
```javascript
{
  "assessments/{assessmentId}": {
    "assessmentId": "assess_001",
    "athleteId": "athlete_001",
    "internId": "user_intern_001", // NEW: Intern who uploads
    
    // Video storage
    "rawVideoGcsUri": "gs://moove-videos/raw/assess_001.mp4", // NEW
    "processedVideoGcsUri": "gs://moove-videos/processed/assess_001.mp4", // NEW
    "videoUrl": "https://storage.googleapis.com/...", // Public URL
    "thumbnailUrl": "https://storage.googleapis.com/...",
    
    // Async workflow status
    "status": "AI_PROCESSING", // UPLOADED | AI_PROCESSING | READY_L1 | READY_L2 | CONFLICT | PUBLISHED
    
    // Progress tracking
    "uploadedAt": Timestamp,
    "aiProcessingStartedAt": Timestamp,
    "aiProcessingCompletedAt": Timestamp,
    "publishedAt": Timestamp,
    
    // Assessment metadata
    "assessmentType": "video",
    "exerciseType": "Squat",
    
    // AI analysis results (populated after processing)
    "aiAnalysis": {
      "confidence": 0.89,
      "keypoints": [...], // MediaPipe output
      "metrics": {
        "squatDepth": 85,
        "kneeAlignment": 92,
        "hipMobility": 78
      }
    },
    
    "createdAt": Timestamp,
    "updatedAt": Timestamp
  }
}
```

### Subcollection: `assessments/{assessmentId}/workflowConfig`
```javascript
{
  "assessments/{assessmentId}/workflowConfig/config": {
    "isLevel2Enabled": false, // Toggle for Level 2 review
    "isPanelMode": false, // Multiple reviewers
    "priority": "MEDIUM", // LOW | MEDIUM | HIGH | URGENT
    "estimatedCompletionTime": "2026-03-26T10:00:00Z",
    "assignedReviewers": ["user_sr_001", "user_sr_002"],
    "createdAt": Timestamp,
    "updatedAt": Timestamp
  }
}
```

### Real-time Status Pulses (same document, just different field)
```javascript
{
  "assessments/{assessmentId}": {
    // ... other fields ...
    
    "statusPulse": {
      "currentStatus": "AI_PROCESSING",
      "progress": 45, // percentage
      "message": "Extracting keypoints...",
      "estimatedCompletion": "2026-03-25T16:00:00Z",
      "lastUpdated": Timestamp
    }
  }
}
```

**Indexes needed:**
- `athleteId` + `status` (for athlete's assessments)
- `status` + `createdAt` (for processing queue)
- `internId` + `uploadedAt` (for intern's uploads)

---

## Task 5: Biomechanical Data & Vector Embeddings

### Collection: `movementData`
```javascript
{
  "movementData/{movementId}": {
    "movementId": "move_001",
    "assessmentId": "assess_001",
    
    // Frame-by-frame coordinates (MediaPipe output)
    "frameCoordinates": {
      "frame_0": {
        "timestamp": 0.0,
        "keypoints": {
          "nose": {"x": 0.5, "y": 0.3, "z": 0.1, "visibility": 0.99},
          "left_shoulder": {"x": 0.4, "y": 0.5, "z": 0.2, "visibility": 0.98},
          // ... 33 keypoints total
        }
      },
      "frame_30": { /* ... */ },
      // Store every Nth frame to reduce size
    },
    
    // Summary metrics extracted from frames
    "summaryMetrics": {
      "exerciseType": "squat",
      "repetitions": 10,
      "jointAngles": {
        "kneeFlexion": {"min": 45, "max": 165, "avg": 105},
        "hipFlexion": {"min": 30, "max": 120, "avg": 75}
      },
      "rangeOfMotion": {
        "left_knee": 120,
        "right_knee": 118
      },
      "symmetry": {
        "left_right": 0.98
      }
    },
    
    // Vertex AI embeddings (768-dim vector as array)
    // Note: Firestore doesn't have native vector search
    // Use Vertex AI Matching Engine for similarity search
    "movementEmbedding": [0.123, -0.456, 0.789, /* ... 768 values */],
    
    "createdAt": Timestamp
  }
}
```

**For Vector Search:**
- Export embeddings to **Vertex AI Matching Engine** for similarity search
- Or use simple distance calculations for small datasets
- Index by `assessmentId` for quick retrieval

**Indexes needed:**
- `assessmentId` (single field)
- Composite: `summaryMetrics.exerciseType` + `createdAt`

---

## Task 6: Clinical Reviews & Holistic Prescriptions

### Collection: `reviews`
```javascript
{
  "reviews/{reviewId}": {
    "reviewId": "review_001",
    "assessmentId": "assess_001",
    "reviewerId": "user_sr_001",
    "reviewLevel": 1, // 1 = Junior Physio, 2 = Senior Physio Panel
    
    // Findings with verified tags from master_taxonomy
    "findingsTags": ["tag_001", "tag_023", "tag_045"],
    
    // Timestamped notes (like video comments)
    "timestampedNotes": {
      "00:15": "Poor knee alignment - valgus collapse",
      "00:32": "Good depth achieved",
      "01:05": "Compensatory hip shift to left"
    },
    
    // Overall findings
    "overallFindings": "Athlete shows good squat depth but demonstrates...",
    "recommendations": [
      "Focus on knee tracking exercises",
      "Strengthen hip abductors",
      "Monitor for pain during training"
    ],
    
    "createdAt": Timestamp
  }
}
```

### Collection: `prescriptions`
```javascript
{
  "prescriptions/{prescriptionId}": {
    "prescriptionId": "rx_001",
    "assessmentId": "assess_001",
    "athleteId": "athlete_001",
    
    // Gatekeeper: must be finalized by SR_PHYSIO
    "finalizedBySrPhysio": "user_sr_001", // Required for PUBLISHED status
    "status": "PUBLISHED", // DRAFT | PENDING_APPROVAL | PUBLISHED
    
    // Holistic prescription components
    "movementPlan": {
      "phase": "strengthening",
      "duration": "4 weeks",
      "exercises": [
        {
          "exerciseId": "ex_001",
          "name": "Wall Squats",
          "sets": 3,
          "reps": 12,
          "frequency": "daily",
          "progressionNotes": "Increase depth weekly"
        },
        {
          "exerciseId": "ex_002",
          "name": "Clamshells",
          "sets": 3,
          "reps": 15,
          "frequency": "3x/week"
        }
      ]
    },
    
    "nutritionPlan": {
      "protein_g_per_kg": 1.8,
      "caloric_surplus": 300,
      "supplements": ["Omega-3", "Vitamin D"],
      "hydration_liters": 3.5,
      "timing": "High protein post-training"
    },
    
    "equipmentSpecs": {
      "required": [
        {
          "item": "Resistance Band",
          "specification": "Medium resistance (15-25 lbs)",
          "purpose": "Hip abduction exercises"
        },
        {
          "item": "Foam Roller",
          "specification": "High density",
          "purpose": "IT band release"
        }
      ]
    },
    
    "coachConstraints": "No jumping or single-leg landing drills for 2 weeks. Limit practice to 60 minutes with 10-min warm-up.",
    
    // Approval workflow
    "draftedBy": "user_jr_002",
    "approvalHistory": [
      {
        "approvedBy": "user_sr_001",
        "timestamp": Timestamp,
        "notes": "Approved with minor modifications"
      }
    ],
    
    "createdAt": Timestamp,
    "publishedAt": Timestamp,
    "updatedAt": Timestamp
  }
}
```

**Security Rule (Gatekeeper):**
```javascript
// Cannot publish without SR_PHYSIO approval
allow update: if request.resource.data.status == 'PUBLISHED' 
  ? (request.resource.data.finalizedBySrPhysio != null 
     && get(/databases/$(database)/documents/users/$(request.resource.data.finalizedBySrPhysio)).data.role == 'SR_PHYSIO')
  : true;
```

**Indexes needed:**
- `assessmentId` + `status`
- `athleteId` + `publishedAt`
- `status` + `createdAt` (for approval queue)

---

## Task 7: Daily Readiness & Compliance Tracking

### Collection: `dailyLogs`
```javascript
{
  "dailyLogs/{logId}": {
    "logId": "log_20260325_athlete_001",
    "athleteId": "athlete_001",
    "date": "2026-03-25",
    
    // Readiness metrics
    "readinessScore": 7, // 0-10 scale
    "fatigue": 4, // 0-10 scale
    "sleep": {
      "hours": 7.5,
      "quality": "good"
    },
    
    // Pain/soreness map
    "sorenessMap": {
      "knee": 3,
      "shoulder": 1,
      "lower_back": 0,
      "hamstring": 2
    },
    
    // Derived metric
    "netPerformance": 3, // readinessScore - fatigue = 7 - 4 = 3
    
    // Additional notes
    "athleteNotes": "Feeling better today, knee less sore",
    
    "createdAt": Timestamp,
    "updatedAt": Timestamp
  }
}
```

### Collection: `complianceTracking`
```javascript
{
  "complianceTracking/{complianceId}": {
    "complianceId": "comp_001",
    "prescriptionId": "rx_001",
    "athleteId": "athlete_001",
    "date": "2026-03-25",
    
    // Completion tracking
    "completionPercentage": 85, // 0-100%
    "exercisesCompleted": 5,
    "exercisesTotal": 6,
    
    // Detailed breakdown
    "exerciseDetails": [
      {
        "exerciseId": "ex_001",
        "completed": true,
        "sets_completed": 3,
        "sets_prescribed": 3,
        "notes": "Felt easier today"
      },
      {
        "exerciseId": "ex_002",
        "completed": false,
        "sets_completed": 0,
        "sets_prescribed": 3,
        "skipped_reason": "Time constraints"
      }
    ],
    
    // Intern/physio notes
    "internNotes": "Good progress, athlete showing improved form",
    
    "createdAt": Timestamp
  }
}
```

### Computed View: Performance vs Pain
**Implementation:** Cloud Function that runs daily or on-demand

```javascript
// Cloud Function: computePerformanceVsPain
export const computePerformanceVsPain = functions.pubsub
  .schedule('0 2 * * *') // Run daily at 2 AM
  .onRun(async (context) => {
    const db = admin.firestore();
    
    // Get last 30 days of data
    const athleteIds = await getActiveAthletes();
    
    for (const athleteId of athleteIds) {
      const logs = await db.collection('dailyLogs')
        .where('athleteId', '==', athleteId)
        .orderBy('date', 'desc')
        .limit(30)
        .get();
      
      const compliance = await db.collection('complianceTracking')
        .where('athleteId', '==', athleteId)
        .orderBy('date', 'desc')
        .limit(30)
        .get();
      
      // Compute trends
      const trends = {
        athleteId,
        last30Days: logs.docs.map(doc => {
          const data = doc.data();
          const compData = compliance.docs.find(c => 
            c.data().date === data.date
          )?.data();
          
          return {
            date: data.date,
            readinessScore: data.readinessScore,
            fatigue: data.fatigue,
            netPerformance: data.netPerformance,
            compliance: compData?.completionPercentage || 0,
            painAreas: Object.keys(data.sorenessMap).filter(
              area => data.sorenessMap[area] > 3
            )
          };
        }),
        averageReadiness: calculateAverage(logs, 'readinessScore'),
        averageCompliance: calculateAverage(compliance, 'completionPercentage'),
        computedAt: admin.firestore.FieldValue.serverTimestamp()
      };
      
      // Store in cache collection for fast retrieval
      await db.collection('analyticsCache')
        .doc(`performanceVsPain_${athleteId}`)
        .set(trends);
    }
  });
```

**Result stored in:** `analyticsCache/performanceVsPain_{athleteId}`

**Indexes needed:**
- `dailyLogs`: `athleteId` + `date`
- `complianceTracking`: `athleteId` + `date`

---

## Task 8: Data Export for Strategic Analytics

### Approach: BigQuery Export + Cloud Function

**1. Enable Firestore to BigQuery export:**
```bash
# Automatically sync Firestore to BigQuery
gcloud firestore databases update --database=(default) \
  --enable-bigquery-export
```

**2. Create anonymized view with Cloud Function:**

```javascript
// Cloud Function: generateAnonymizedResearchData
export const generateAnonymizedResearchData = functions.https
  .onRequest(async (req, res) => {
    const db = admin.firestore();
    
    // Fetch all athletes
    const athletesSnapshot = await db.collection('athletes').get();
    
    const anonymizedData = [];
    
    for (const athleteDoc of athletesSnapshot.docs) {
      const athlete = athleteDoc.data();
      
      // Get user data for age calculation
      const userDoc = await db.collection('users')
        .doc(athlete.userId)
        .get();
      const user = userDoc.data();
      
      // Get assessments and movement data
      const assessments = await db.collection('assessments')
        .where('athleteId', '==', athlete.id)
        .get();
      
      const movementData = [];
      const verifiedTags = [];
      
      for (const assessmentDoc of assessments.docs) {
        const assessment = assessmentDoc.data();
        
        // Get movement data
        const movement = await db.collection('movementData')
          .where('assessmentId', '==', assessment.assessmentId)
          .get();
        
        movementData.push(...movement.docs.map(m => m.data().summaryMetrics));
        
        // Get reviews with verified tags
        const reviews = await db.collection('reviews')
          .where('assessmentId', '==', assessment.assessmentId)
          .get();
        
        for (const reviewDoc of reviews.docs) {
          const review = reviewDoc.data();
          verifiedTags.push(...review.findingsTags);
        }
      }
      
      // Calculate age (no PII)
      const age = calculateAge(user.dateOfBirth);
      
      // Anonymized record
      anonymizedData.push({
        anonAthleteId: hashId(athlete.id), // One-way hash
        age,
        sport: athlete.sport,
        position: athlete.position,
        
        // Aggregated joint angles
        jointAngles: aggregateJointAngles(movementData),
        
        // Only verified diagnosis tags
        verifiedDiagnosisTags: await getVerifiedTagNames(verifiedTags),
        
        // Summary stats
        totalAssessments: assessments.size,
        avgRangeOfMotion: calculateAvgROM(movementData),
        
        generatedAt: admin.firestore.Timestamp.now()
      });
    }
    
    // Store in a separate collection
    const batch = db.batch();
    anonymizedData.forEach((record, index) => {
      const docRef = db.collection('anonymizedResearchData').doc(`record_${index}`);
      batch.set(docRef, record);
    });
    await batch.commit();
    
    res.json({
      success: true,
      recordsGenerated: anonymizedData.length
    });
  });
```

**3. Manual query in Firestore console or via API:**
```javascript
// Frontend: Fetch anonymized data for analysis
const analyticsData = await db.collection('anonymizedResearchData').get();
const data = analyticsData.docs.map(doc => doc.data());

// Export to CSV or JSON for strategic analysis
exportToCSV(data, 'anonymized_research_data.csv');
```

**Alternative: Use BigQuery directly for complex analytics:**
```sql
-- BigQuery query on exported Firestore data
SELECT 
  data__age AS age,
  data__sport AS sport,
  data__position AS position,
  AVG(CAST(JSON_EXTRACT_SCALAR(data__jointAngles, '$.kneeFlexion.avg') AS FLOAT64)) AS avg_knee_flexion,
  COUNT(*) AS total_assessments
FROM `project.dataset.athletes_raw_latest`
WHERE data__age IS NOT NULL
GROUP BY age, sport, position
```

**Indexes needed:**
- `anonymizedResearchData`: No specific index (read-heavy, can scan)

---

## Summary: Firestore vs PostgreSQL Tradeoffs

| Feature | PostgreSQL (Deleted) | Firestore (Current) |
|---------|---------------------|---------------------|
| **Cost** | $10-15/month | $0 (free tier) ✅ |
| **Setup** | Complex (proxy needed) | Simple (serverless) ✅ |
| **Vector Search** | Native (pgvector) | Via Vertex AI ⚠️ |
| **Complex Queries** | SQL joins, views | Denormalized data ⚠️ |
| **Real-time** | Need additional setup | Built-in ✅ |
| **Scalability** | Manual management | Auto-scales ✅ |
| **Analytics** | Native views | Export to BigQuery ⚠️ |

---

## Next Steps

1. ✅ Schema designed (this document)
2. Update `firestore.rules` with security rules
3. Create `firestore.indexes.json` with all indexes
4. Deploy Cloud Functions for computed views
5. Create seed data for testing
6. Deploy: `firebase deploy --only firestore,functions`

All tasks adapted to Firestore! Ready to implement. 🚀
