// Firestore Seed Data Script
// Run: node seed-firestore.js

const admin = require('firebase-admin');

// Initialize Firebase Admin SDK
// Option 1: Using service account key (download from Firebase Console)
// const serviceAccount = require('./serviceAccountKey.json');
// admin.initializeApp({
//   credential: admin.credential.cert(serviceAccount)
// });

// Option 2: Using Application Default Credentials (if gcloud configured)
admin.initializeApp({
  projectId: 'watch-mail-trial'
});

const db = admin.firestore();
const timestamp = admin.firestore.Timestamp.now();

async function seedData() {
  console.log('Starting Firestore seed...');

  try {
    // ========== Task 2: Core Entities ==========
    
    // Organizations
    await db.collection('organizations').doc('org_001').set({
      id: 'org_001',
      name: 'Mumbai Sports Institute',
      type: 'INSTITUTE',
      isCofounder: true,
      createdAt: timestamp,
      updatedAt: timestamp
    });

    await db.collection('organizations').doc('org_002').set({
      id: 'org_002',
      name: 'Chennai Cricket Club',
      type: 'CLUB',
      isCofounder: false,
      createdAt: timestamp,
      updatedAt: timestamp
    });
    console.log('✓ Organizations seeded');

    // Users
    await db.collection('users').doc('user_sr_001').set({
      id: 'user_sr_001',
      email: 'dr.sharma@institute.com',
      fullName: 'Dr. Anita Sharma',
      role: 'SR_PHYSIO',
      orgId: 'org_001',
      phone: '+91-9876543210',
      dateOfBirth: '1985-03-15',
      avatar: 'https://i.pravatar.cc/150?img=1',
      status: 'active',
      createdAt: timestamp,
      updatedAt: timestamp,
      lastLoginAt: timestamp
    });

    await db.collection('users').doc('user_jr_001').set({
      id: 'user_jr_001',
      email: 'priya.patel@institute.com',
      fullName: 'Priya Patel',
      role: 'JR_PHYSIO',
      orgId: 'org_001',
      phone: '+91-9876543211',
      dateOfBirth: '1992-07-20',
      avatar: 'https://i.pravatar.cc/150?img=2',
      status: 'active',
      createdAt: timestamp,
      updatedAt: timestamp,
      lastLoginAt: timestamp
    });

    await db.collection('users').doc('user_intern_001').set({
      id: 'user_intern_001',
      email: 'raj.intern@institute.com',
      fullName: 'Raj Kumar',
      role: 'INTERN',
      orgId: 'org_001',
      phone: '+91-9876543212',
      dateOfBirth: '2000-01-10',
      avatar: 'https://i.pravatar.cc/150?img=3',
      status: 'active',
      createdAt: timestamp,
      updatedAt: timestamp,
      lastLoginAt: timestamp
    });

    await db.collection('users').doc('user_athlete_001').set({
      id: 'user_athlete_001',
      email: 'virat.athlete@cricket.com',
      fullName: 'Virat Singh',
      role: 'ATHLETE',
      orgId: 'org_002',
      phone: '+91-9876543213',
      dateOfBirth: '1998-11-05',
      avatar: 'https://i.pravatar.cc/150?img=4',
      status: 'active',
      createdAt: timestamp,
      updatedAt: timestamp,
      lastLoginAt: timestamp
    });
    console.log('✓ Users seeded');

    // Athletes
    await db.collection('athletes').doc('athlete_001').set({
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
      createdAt: timestamp,
      updatedAt: timestamp
    });
    console.log('✓ Athletes seeded');

    // ========== Task 3: Taxonomy ==========
    
    await db.collection('masterTaxonomy').doc('tag_001').set({
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
      createdAt: timestamp,
      verifiedAt: timestamp
    });

    await db.collection('masterTaxonomy').doc('tag_002').set({
      tagId: 'tag_002',
      category: 'EXERCISE',
      tagName: 'Single Leg Squat',
      isVerified: true,
      suggestedBy: 'user_jr_001',
      verifiedBy: 'user_sr_001',
      metadata: {
        description: 'Unilateral lower body strengthening exercise'
      },
      createdAt: timestamp,
      verifiedAt: timestamp
    });

    await db.collection('masterTaxonomy').doc('tag_003').set({
      tagId: 'tag_003',
      category: 'NUTRITION',
      tagName: 'High Protein - Recovery Phase',
      isVerified: true,
      suggestedBy: 'user_sr_001',
      verifiedBy: 'user_sr_001',
      metadata: {
        description: 'Increased protein intake for tissue repair'
      },
      createdAt: timestamp,
      verifiedAt: timestamp
    });
    console.log('✓ Master Taxonomy seeded');

    await db.collection('tagSuggestions').doc('sugg_001').set({
      suggestionId: 'sugg_001',
      category: 'EXERCISE',
      tagName: 'Eccentric Calf Raises',
      suggestedBy: 'user_intern_001',
      status: 'PENDING',
      reviewedBy: null,
      reviewNotes: null,
      reviewedAt: null,
      createdAt: timestamp
    });

    await db.collection('tagSuggestions').doc('sugg_002').set({
      suggestionId: 'sugg_002',
      category: 'EQUIPMENT',
      tagName: 'TheraBand - Heavy Resistance',
      suggestedBy: 'user_jr_001',
      status: 'APPROVED',
      reviewedBy: 'user_sr_001',
      reviewNotes: 'Good addition for strength training',
      reviewedAt: timestamp,
      createdAt: timestamp
    });
    console.log('✓ Tag Suggestions seeded');

    // ========== Task 4: Assessments ==========
    
    const futureDate = admin.firestore.Timestamp.fromDate(
      new Date(Date.now() + 24*60*60*1000)
    );

    await db.collection('assessments').doc('assess_001').set({
      assessmentId: 'assess_001',
      athleteId: 'athlete_001',
      internId: 'user_intern_001',
      rawVideoGcsUri: 'gs://moove-videos/raw/assess_001.mp4',
      processedVideoGcsUri: 'gs://moove-videos/processed/assess_001.mp4',
      videoUrl: 'https://storage.googleapis.com/moove-videos/assess_001.mp4',
      thumbnailUrl: 'https://storage.googleapis.com/moove-videos/thumbs/assess_001.jpg',
      status: 'READY_L1',
      uploadedAt: timestamp,
      aiProcessingStartedAt: timestamp,
      aiProcessingCompletedAt: timestamp,
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
        estimatedCompletion: futureDate,
        lastUpdated: timestamp
      },
      createdAt: timestamp,
      updatedAt: timestamp
    });

    await db.collection('assessments').doc('assess_001')
      .collection('workflowConfig').doc('config').set({
        isLevel2Enabled: false,
        isPanelMode: false,
        priority: 'MEDIUM',
        estimatedCompletionTime: futureDate,
        assignedReviewers: ['user_jr_001'],
        createdAt: timestamp,
        updatedAt: timestamp
      });
    console.log('✓ Assessments seeded');

    // ========== Task 5: Movement Data ==========
    
    const embedding = new Array(768).fill(0).map(() => Math.random());
    
    await db.collection('movementData').doc('move_001').set({
      movementId: 'move_001',
      assessmentId: 'assess_001',
      frameCoordinates: {
        frame_0: {
          timestamp: 0.0,
          keypoints: {
            nose: {x: 0.5, y: 0.3, z: 0.1, visibility: 0.99},
            left_shoulder: {x: 0.4, y: 0.5, z: 0.2, visibility: 0.98},
            right_shoulder: {x: 0.6, y: 0.5, z: 0.2, visibility: 0.97}
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
      movementEmbedding: embedding,
      createdAt: timestamp
    });
    console.log('✓ Movement Data seeded');

    // ========== Task 6: Reviews & Prescriptions ==========
    
    await db.collection('reviews').doc('review_001').set({
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
      overallFindings: 'Athlete shows good squat depth but demonstrates knee valgus and compensatory patterns.',
      recommendations: [
        'Focus on knee tracking exercises',
        'Strengthen hip abductors',
        'Add proprioceptive training'
      ],
      createdAt: timestamp
    });
    console.log('✓ Reviews seeded');

    await db.collection('prescriptions').doc('rx_001').set({
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
            frequency: 'daily',
            progression: 'Add resistance band after week 2'
          },
          {
            exerciseId: 'ex_002',
            name: 'Clamshells',
            sets: 3,
            reps: 15,
            frequency: 'daily',
            progression: 'Progress to standing abduction'
          }
        ]
      },
      nutritionPlan: {
        protein_g_per_kg: 1.8,
        caloric_surplus: 300,
        hydration_liters: 3.5,
        supplements: ['Omega-3', 'Vitamin D', 'Collagen']
      },
      equipmentSpecs: {
        required: [
          {
            item: 'Resistance Band',
            specification: 'Medium resistance (15-25 lbs)',
            quantity: 1
          },
          {
            item: 'Foam Roller',
            specification: 'Standard density, 36 inches',
            quantity: 1
          }
        ]
      },
      coachConstraints: 'No jumping drills for 2 weeks. Limit sprint distance to 50m.',
      draftedBy: 'user_jr_001',
      approvalHistory: [
        {
          approvedBy: 'user_sr_001',
          timestamp: timestamp,
          notes: 'Approved with good exercise selection'
        }
      ],
      createdAt: timestamp,
      publishedAt: timestamp,
      updatedAt: timestamp
    });
    console.log('✓ Prescriptions seeded');

    // ========== Task 7: Daily Tracking ==========
    
    await db.collection('dailyLogs').doc('log_20260325_athlete_001').set({
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
      athleteNotes: 'Feeling better today, shoulder less painful',
      createdAt: timestamp,
      updatedAt: timestamp
    });

    await db.collection('dailyLogs').doc('log_20260324_athlete_001').set({
      logId: 'log_20260324_athlete_001',
      athleteId: 'athlete_001',
      date: '2026-03-24',
      readinessScore: 5,
      fatigue: 6,
      sleep: {
        hours: 6.0,
        quality: 'fair'
      },
      sorenessMap: {
        knee: 4,
        shoulder: 3,
        lower_back: 1,
        hamstring: 3
      },
      netPerformance: -1,
      athleteNotes: 'Tough day, more soreness than expected',
      createdAt: timestamp,
      updatedAt: timestamp
    });
    console.log('✓ Daily Logs seeded');

    await db.collection('complianceTracking').doc('comp_001').set({
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
          sets_prescribed: 3,
          notes: 'Good form'
        },
        {
          exerciseId: 'ex_002',
          completed: true,
          sets_completed: 2,
          sets_prescribed: 3,
          notes: 'Felt tight, did 2 sets'
        }
      ],
      internNotes: 'Good progress, athlete motivated',
      createdAt: timestamp
    });
    console.log('✓ Compliance Tracking seeded');

    // ========== Task 8: Analytics Cache ==========
    
    const thirtyDaysAgo = admin.firestore.Timestamp.fromDate(
      new Date(Date.now() - 30*24*60*60*1000)
    );

    await db.collection('analyticsCache').doc('analytics_athlete_001').set({
      athleteId: 'athlete_001',
      period: '30_days',
      computed: {
        performanceTrend: {
          slope: 0.15,
          direction: 'improving',
          dataPoints: [
            {date: '2026-02-25', value: 3},
            {date: '2026-03-04', value: 4},
            {date: '2026-03-11', value: 5},
            {date: '2026-03-18', value: 6},
            {date: '2026-03-25', value: 7}
          ]
        },
        painTrend: {
          slope: -0.12,
          direction: 'decreasing',
          dataPoints: [
            {date: '2026-02-25', value: 6},
            {date: '2026-03-04', value: 5},
            {date: '2026-03-11', value: 4},
            {date: '2026-03-18', value: 3},
            {date: '2026-03-25', value: 2}
          ]
        },
        complianceRate: 0.82,
        averageReadiness: 6.5,
        recoveryVelocity: 'on_track'
      },
      computedAt: timestamp,
      computedBy: 'cloud-function-daily-job',
      periodStart: thirtyDaysAgo,
      periodEnd: timestamp
    });
    console.log('✓ Analytics Cache seeded');

    console.log('\n🎉 Firestore seed completed successfully!');
    console.log('\nSeeded collections:');
    console.log('  - organizations (2)');
    console.log('  - users (4)');
    console.log('  - athletes (1)');
    console.log('  - masterTaxonomy (3)');
    console.log('  - tagSuggestions (2)');
    console.log('  - assessments (1 + 1 subcollection)');
    console.log('  - movementData (1)');
    console.log('  - reviews (1)');
    console.log('  - prescriptions (1)');
    console.log('  - dailyLogs (2)');
    console.log('  - complianceTracking (1)');
    console.log('  - analyticsCache (1)');
    console.log('\nTotal: 20+ documents across 12 collections');

  } catch (error) {
    console.error('Error seeding Firestore:', error);
    process.exit(1);
  }

  process.exit(0);
}

seedData();
