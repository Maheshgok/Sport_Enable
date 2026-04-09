# Firebase Architecture for Moove MVP

## Overview

This MVP uses **Firebase** for ONLY the video upload and analysis feature. Everything else (user profiles, dashboards, stats) uses **mock data** from `src/data/`.

### Cost: FREE Tier Limits
- **Firestore**: 1GB storage, 50K reads/day
- **Storage**: 5GB storage, 1GB downloads/day  
- **Hosting**: 10GB storage, 360MB/day bandwidth

For a demo MVP, this should be more than sufficient.

---

## Architecture

```
Frontend (React)
├── Mock Data (90%) ← All dashboards, profiles, stats
└── Firebase Integration (10%) ↓

Firebase Services
├── Storage ← Video files
├── Firestore ← Video metadata + Analysis results
└── Hosting ← Static site deployment
```

---

## Firestore Schema

### Collection: `videos`

Stores video metadata and analysis results.

```javascript
{
  "videos/{videoId}": {
    // Upload info
    "fileName": "rehab_exercise_20260325.mp4",
    "fileSize": 15728640, // bytes
    "videoUrl": "https://storage.firebase.com/.../videos/...",
    "thumbnailUrl": "https://...", // optional
    
    // Metadata
    "athleteId": "a1111111-1111-1111-1111-111111111111", // from mock data
    "exerciseType": "squat",
    "uploadedAt": Timestamp,
    
    // Processing status
    "status": "processing" | "completed" | "failed",
    "analysisComplete": false,
    
    // Analysis results (populated after processing)
    "analysis": {
      "movements": {
        "squatDepth": 85,
        "kneeAlignment": 92,
        "hipMobility": 78
      },
      "recommendations": [
        "Increase depth gradually",
        "Focus on knee tracking"
      ],
      "riskScore": "low" | "medium" | "high",
      "confidence": 0.89
    },
    "analyzedAt": Timestamp
  }
}
```

### Indexes Required

None for MVP. Add if queries become slow:
- `athleteId` + `uploadedAt` (descending)
- `status` + `uploadedAt` (descending)

---

## Storage Structure

```
/videos/
  ├── {timestamp}_{filename}.mp4
  ├── {timestamp}_{filename}.mp4
  └── ...
```

Max file size: 100MB (configurable in `storage.rules`)

---

## Integration with Media Pipeline

The `analyzeVideo()` function in `src/firebase/videoService.js` currently returns mock data. 

### TODO: Replace with actual API call

```javascript
// Example: Google Cloud Video Intelligence API
import { VideoIntelligenceServiceClient } from '@google-cloud/video-intelligence';

export const analyzeVideo = async (videoUrl) => {
  const client = new VideoIntelligenceServiceClient();
  
  const [operation] = await client.annotateVideo({
    inputUri: videoUrl,
    features: ['LABEL_DETECTION', 'SHOT_CHANGE_DETECTION']
  });
  
  const [results] = await operation.promise();
  
  // Transform results into your schema
  return transformAnalysisResults(results);
};
```

---

## Deployment Steps

### 1. Get Firebase Config

```bash
# Go to Firebase Console
https://console.firebase.google.com/project/watch-mail-trial/settings/general

# Copy your config values and update:
src/firebase/config.js
```

### 2. Install Dependencies

```bash
npm install firebase
```

### 3. Deploy Firestore Rules & Indexes

```bash
npx firebase deploy --only firestore
```

### 4. Deploy Storage Rules

```bash
npx firebase deploy --only storage
```

### 5. Deploy Frontend

```bash
npm run build
npx firebase deploy --only hosting
```

---

## Security Notes (For Production)

⚠️ Current rules allow anonymous access for demo purposes.

For production:
1. Enable Firebase Authentication
2. Update `firestore.rules` to require auth
3. Update `storage.rules` to require auth
4. Add user permissions (athlete can only see their videos)

---

## Mock Data vs Real Data

| Feature | Data Source |
|---------|-------------|
| User Profiles | Mock (`src/data/mockData.js`) |
| Dashboard Stats | Mock |
| Exercise History | Mock |
| Team Members | Mock |
| **Video Upload** | **Firebase Storage** ✅ |
| **Video Analysis** | **Firestore** ✅ |

Only video upload/analysis hits Firebase. Everything else is static.
