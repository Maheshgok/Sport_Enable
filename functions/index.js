const functions = require('firebase-functions');
const admin = require('firebase-admin');
admin.initializeApp();

const db = admin.firestore();

// ======================================================================
// Task 7: Performance vs Pain - Daily Computation
// ======================================================================

/**
 * Computes performance vs pain trends for all active athletes
 * Runs daily at 2 AM
 */
exports.computePerformanceVsPain = functions
  .region('asia-south1')
  .pubsub
  .schedule('0 2 * * *')
  .timeZone('Asia/Kolkata')
  .onRun(async (context) => {
    console.log('Starting daily performance vs pain computation...');
    
    try {
      // Get all active athletes
      const athletesSnapshot = await db.collection('athletes')
        .where('status', 'in', ['active', 'recovering'])
        .get();
      
      const promises = athletesSnapshot.docs.map(async (athleteDoc) => {
        const athleteId = athleteDoc.id;
        
        // Get last 30 days of daily logs
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        const dateStr = thirtyDaysAgo.toISOString().split('T')[0];
        
        const logsSnapshot = await db.collection('dailyLogs')
          .where('athleteId', '==', athleteId)
          .where('date', '>=', dateStr)
          .orderBy('date', 'desc')
          .get();
        
        const complianceSnapshot = await db.collection('complianceTracking')
          .where('athleteId', '==', athleteId)
          .where('date', '>=', dateStr)
          .orderBy('date', 'desc')
          .get();
        
        // Build compliance map for quick lookup
        const complianceMap = {};
        complianceSnapshot.docs.forEach(doc => {
          const data = doc.data();
          complianceMap[data.date] = data;
        });
        
        // Compute trend data
        const trends = logsSnapshot.docs.map(logDoc => {
          const log = logDoc.data();
          const compliance = complianceMap[log.date];
          
          // Extract pain areas (soreness > 3)
          const painAreas = Object.keys(log.sorenessMap || {})
            .filter(area => log.sorenessMap[area] > 3);
          
          return {
            date: log.date,
            readinessScore: log.readinessScore || 0,
            fatigue: log.fatigue || 0,
            netPerformance: (log.readinessScore || 0) - (log.fatigue || 0),
            compliance: compliance?.completionPercentage || 0,
            painAreas: painAreas,
            painLevel: Math.max(...Object.values(log.sorenessMap || {}), 0)
          };
        });
        
        // Calculate averages
        const avgReadiness = trends.reduce((sum, t) => sum + t.readinessScore, 0) / trends.length;
        const avgFatigue = trends.reduce((sum, t) => sum + t.fatigue, 0) / trends.length;
        const avgCompliance = trends.reduce((sum, t) => sum + t.compliance, 0) / trends.length;
        const avgPainLevel = trends.reduce((sum, t) => sum + t.painLevel, 0) / trends.length;
        
        // Store in analytics cache
        await db.collection('analyticsCache')
          .doc(`performanceVsPain_${athleteId}`)
          .set({
            athleteId,
            last30Days: trends,
            summary: {
              averageReadiness: Math.round(avgReadiness * 10) / 10,
              averageFatigue: Math.round(avgFatigue * 10) / 10,
              averageCompliance: Math.round(avgCompliance * 10) / 10,
              averagePainLevel: Math.round(avgPainLevel * 10) / 10,
              trend: calculateTrend(trends)
            },
            computedAt: admin.firestore.FieldValue.serverTimestamp()
          });
        
        console.log(`Computed performance vs pain for athlete: ${athleteId}`);
      });
      
      await Promise.all(promises);
      console.log(`Completed computation for ${promises.length} athletes`);
      
      return null;
    } catch (error) {
      console.error('Error computing performance vs pain:', error);
      throw error;
    }
  });

// Helper function to calculate trend direction
function calculateTrend(trends) {
  if (trends.length < 2) return 'stable';
  
  const recent = trends.slice(0, 7); // Last 7 days
  const previous = trends.slice(7, 14); // Previous 7 days
  
  if (recent.length === 0 || previous.length === 0) return 'stable';
  
  const recentAvg = recent.reduce((sum, t) => sum + t.netPerformance, 0) / recent.length;
  const previousAvg = previous.reduce((sum, t) => sum + t.netPerformance, 0) / previous.length;
  
  const change = ((recentAvg - previousAvg) / previousAvg) * 100;
  
  if (change > 10) return 'improving';
  if (change < -10) return 'declining';
  return 'stable';
}

// ======================================================================
// Task 8: Anonymized Research Data Generation
// ======================================================================

/**
 * Generates anonymized research data for strategic analytics
 * Called via HTTP or manually triggered
 */
exports.generateAnonymizedResearchData = functions
  .region('asia-south1')
  .https.onRequest(async (req, res) => {
  console.log('Starting anonymized research data generation...');
  
  try {
    // Get all athletes
    const athletesSnapshot = await db.collection('athletes').get();
    
    const anonymizedRecords = [];
    
    for (const athleteDoc of athletesSnapshot.docs) {
      const athlete = athleteDoc.data();
      
      // Get user data for age calculation
      const userDoc = await db.collection('users').doc(athlete.userId).get();
      if (!userDoc.exists) continue;
      
      const user = userDoc.data();
      
      // Calculate age (no PII)
      const age = calculateAge(user.dateOfBirth);
      
      // Get all assessments for this athlete
      const assessmentsSnapshot = await db.collection('assessments')
        .where('athleteId', '==', athlete.id)
        .get();
      
      if (assessmentsSnapshot.empty) continue;
      
      const jointAnglesArray = [];
      const verifiedTagIds = [];
      const romValues = [];
      
      // Process each assessment
      for (const assessmentDoc of assessmentsSnapshot.docs) {
        const assessment = assessmentDoc.data();
        
        // Get movement data
        const movementSnapshot = await db.collection('movementData')
          .where('assessmentId', '==', assessment.assessmentId)
          .get();
        
        movementSnapshot.docs.forEach(movDoc => {
          const movement = movDoc.data();
          if (movement.summaryMetrics?.jointAngles) {
            jointAnglesArray.push(movement.summaryMetrics.jointAngles);
          }
          if (movement.summaryMetrics?.rangeOfMotion) {
            romValues.push(movement.summaryMetrics.rangeOfMotion);
          }
        });
        
        // Get reviews with verified tags only
        const reviewsSnapshot = await db.collection('reviews')
          .where('assessmentId', '==', assessment.assessmentId)
          .get();
        
        reviewsSnapshot.docs.forEach(reviewDoc => {
          const review = reviewDoc.data();
          if (review.findingsTags) {
            verifiedTagIds.push(...review.findingsTags);
          }
        });
      }
      
      // Get verified tag names
      const verifiedTagNames = await getVerifiedTagNames([...new Set(verifiedTagIds)]);
      
      // Aggregate joint angles
      const aggregatedJointAngles = aggregateJointAngles(jointAnglesArray);
      
      // Calculate average ROM
      const avgROM = romValues.length > 0
        ? Object.values(romValues.reduce((acc, rom) => {
            Object.keys(rom).forEach(joint => {
              acc[joint] = (acc[joint] || 0) + rom[joint];
            });
            return acc;
          }, {})).reduce((sum, val) => sum + val, 0) / romValues.length
        : 0;
      
      // Create anonymized record
      anonymizedRecords.push({
        anonAthleteId: hashId(athlete.id),
        age,
        sport: athlete.sport,
        position: athlete.position || 'Unknown',
        jointAngles: aggregatedJointAngles,
        verifiedDiagnosisTags: verifiedTagNames,
        totalAssessments: assessmentsSnapshot.size,
        avgRangeOfMotion: Math.round(avgROM * 10) / 10,
        generatedAt: admin.firestore.Timestamp.now()
      });
    }
    
    // Store in Firestore
    const batch = db.batch();
    anonymizedRecords.forEach((record, index) => {
      const docRef = db.collection('anonymizedResearchData').doc(`record_${Date.now()}_${index}`);
      batch.set(docRef, record);
    });
    await batch.commit();
    
    console.log(`Generated ${anonymizedRecords.length} anonymized records`);
    
    res.json({
      success: true,
      recordsGenerated: anonymizedRecords.length,
      message: 'Anonymized research data generated successfully'
    });
    
  } catch (error) {
    console.error('Error generating anonymized research data:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// ======================================================================
// Task 4: Assessment Status Update Trigger
// ======================================================================

/**
 * Updates status pulse when assessment status changes
 * Triggered on assessment document writes
 */
exports.onAssessmentStatusChange = functions
  .region('asia-south1')
  .firestore
  .document('assessments/{assessmentId}')
  .onWrite(async (change, context) => {
    const assessmentId = context.params.assessmentId;
    
    if (!change.after.exists) return null; // Document deleted
    
    const newData = change.after.data();
    const oldData = change.before.exists ? change.before.data() : {};
    
    // Check if status changed
    if (newData.status === oldData.status) return null;
    
    console.log(`Assessment ${assessmentId} status changed: ${oldData.status} -> ${newData.status}`);
    
    // Update status pulse for real-time updates
    const statusMessages = {
      'UPLOADED': 'Video uploaded successfully',
      'AI_PROCESSING': 'AI analysis in progress...',
      'READY_L1': 'Ready for Level 1 review',
      'READY_L2': 'Ready for Level 2 review',
      'CONFLICT': 'Review conflict - needs panel',
      'PUBLISHED': 'Assessment complete'
    };
    
    const estimatedTimes = {
      'UPLOADED': 5, // 5 minutes for AI processing
      'AI_PROCESSING': 3,
      'READY_L1': 1440, // 24 hours for review
      'READY_L2': 720, // 12 hours for senior review
      'CONFLICT': 1440,
      'PUBLISHED': 0
    };
    
    const now = new Date();
    const estimatedCompletion = new Date(now.getTime() + (estimatedTimes[newData.status] || 0) * 60000);
    
    await change.after.ref.update({
      statusPulse: {
        currentStatus: newData.status,
        progress: calculateProgress(newData.status),
        message: statusMessages[newData.status] || 'Processing...',
        estimatedCompletion: admin.firestore.Timestamp.fromDate(estimatedCompletion),
        lastUpdated: admin.firestore.FieldValue.serverTimestamp()
      }
    });
    
    return null;
  });

// Helper: Calculate progress percentage based on status
function calculateProgress(status) {
  const progressMap = {
    'UPLOADED': 10,
    'AI_PROCESSING': 30,
    'READY_L1': 50,
    'READY_L2': 75,
    'CONFLICT': 60,
    'PUBLISHED': 100
  };
  return progressMap[status] || 0;
}

// Helper: Calculate age from date of birth
function calculateAge(dob) {
  if (!dob) return null;
  const birthDate = new Date(dob);
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age;
}

// Helper: One-way hash for anonymous IDs
function hashId(id) {
  const crypto = require('crypto');
  return crypto.createHash('sha256').update(id).digest('hex').substring(0, 16);
}

// Helper: Get verified tag names from IDs
async function getVerifiedTagNames(tagIds) {
  if (tagIds.length === 0) return [];
  
  const tagNames = [];
  const chunks = chunkArray(tagIds, 10); // Firestore 'in' limit is 10
  
  for (const chunk of chunks) {
    const tagsSnapshot = await db.collection('masterTaxonomy')
      .where(admin.firestore.FieldPath.documentId(), 'in', chunk)
      .where('isVerified', '==', true)
      .get();
    
    tagsSnapshot.docs.forEach(doc => {
      tagNames.push(doc.data().tagName);
    });
  }
  
  return [...new Set(tagNames)]; // Remove duplicates
}

// Helper: Aggregate joint angles from multiple measurements
function aggregateJointAngles(jointAnglesArray) {
  if (jointAnglesArray.length === 0) return {};
  
  const aggregated = {};
  
  jointAnglesArray.forEach(angles => {
    Object.keys(angles).forEach(joint => {
      if (!aggregated[joint]) {
        aggregated[joint] = { min: [], max: [], avg: [] };
      }
      if (angles[joint].min !== undefined) aggregated[joint].min.push(angles[joint].min);
      if (angles[joint].max !== undefined) aggregated[joint].max.push(angles[joint].max);
      if (angles[joint].avg !== undefined) aggregated[joint].avg.push(angles[joint].avg);
    });
  });
  
  // Calculate averages
  const result = {};
  Object.keys(aggregated).forEach(joint => {
    result[joint] = {
      min: avg(aggregated[joint].min),
      max: avg(aggregated[joint].max),
      avg: avg(aggregated[joint].avg)
    };
  });
  
  return result;
}

// Helper: Calculate average
function avg(arr) {
  if (arr.length === 0) return 0;
  return Math.round((arr.reduce((sum, val) => sum + val, 0) / arr.length) * 10) / 10;
}

// Helper: Split array into chunks
function chunkArray(array, size) {
  const chunks = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
}
