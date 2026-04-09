# 🚀 Moove MVP - Complete Deployment Guide

## ✅ What's Set Up

- ✅ Cloud SQL deleted (saves $10-15/month)
- ✅ Firebase initialized (project: watch-mail-trial)
- ✅ Firestore & Storage configured
- ✅ Video upload service created
- ✅ Firebase SDK installed

---

## 📋 Pre-Deployment Checklist

### 1. Get Your Firebase Config

1. Go to [Firebase Console](https://console.firebase.google.com/project/watch-mail-trial/settings/general)
2. Scroll to "Your apps" section
3. Click "Web app" (or add a new web app if none exists)
4. Copy the config object

### 2. Update Firebase Config File

Edit `src/firebase/config.js` and replace placeholders:

```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY_HERE",
  authDomain: "watch-mail-trial.firebaseapp.com",
  projectId: "watch-mail-trial",
  storageBucket: "watch-mail-trial.appspot.com",
  messagingSenderId: "YOUR_ID_HERE",
  appId: "YOUR_APP_ID_HERE"
};
```

---

## 🔥 Deploy to Firebase

### Step 1: Login to Firebase

```powershell
npx firebase login
```

### Step 2: Deploy Firestore & Storage Rules

```powershell
npx firebase deploy --only firestore,storage
```

This sets up:
- Firestore database with video schema
- Storage bucket for video files
- Security rules (open for demo)

### Step 3: Build & Deploy Frontend

```powershell
npm run deploy
```

Or manually:
```powershell
npm run build
npx firebase deploy --only hosting
```

### Step 4: Test Your Deployment

Visit: `https://watch-mail-trial.web.app`

Or your custom domain (if configured).

---

## 🌐 Optional: Set Up Custom Domain (moove.edgechurn.ai)

### 1. Add Domain in Firebase Console

1. Go to [Firebase Hosting](https://console.firebase.google.com/project/watch-mail-trial/hosting)
2. Click "Add custom domain"
3. Enter: `moove.edgechurn.ai`

### 2. Update DNS

Add these records where edgechurn.ai DNS is managed:

**For verification (one-time):**
```
Type: TXT
Name: moove
Value: [provided by Firebase]
```

**For actual connection:**
```
Type: A
Name: moove
Value: [IP provided by Firebase]

Type: A
Name: moove
Value: [2nd IP provided by Firebase]
```

Firebase will auto-provision SSL certificate.

---

## 🎥 Video Upload Feature Integration

The video upload feature is ready to integrate into your UI.

### Example Usage

```javascript
import { uploadVideo, saveVideoMetadata, analyzeVideo } from '@/firebase/videoService';

// In your component
const handleVideoUpload = async (file) => {
  try {
    // 1. Upload video to Storage
    const videoUrl = await uploadVideo(file, (progress) => {
      console.log(`Upload: ${progress}%`);
    });
    
    // 2. Save metadata to Firestore
    const videoId = await saveVideoMetadata({
      fileName: file.name,
      fileSize: file.size,
      videoUrl: videoUrl,
      athleteId: currentAthleteId, // from mock data
      exerciseType: 'squat'
    });
    
    // 3. Trigger analysis (mock for now)
    const analysisResults = await analyzeVideo(videoUrl);
    
    // 4. Update with results
    await updateVideoAnalysis(videoId, analysisResults);
    
    console.log('Video processed!', videoId);
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

---

## 💰 Cost Estimate

### Firebase FREE Tier (Sufficient for MVP Demo)
- Firestore: 1GB storage, 50K reads/day
- Storage: 5GB storage, 1GB download/day  
- Hosting: 10GB storage, 360MB bandwidth/day

**Expected usage for demo:**
- ~10 video uploads/day = ~50MB
- ~100 page views/day = ~10MB bandwidth
- **Cost: $0/month** ✅

Compare to:
- Cloud SQL: ~$15/month ❌

**Savings: $15/month or $180/year**

---

## 🔧 For Later: Real Video Analysis Integration

Current `analyzeVideo()` returns mock data. To integrate real AI:

### Option 1: Google Cloud Video Intelligence API

```bash
npm install @google-cloud/video-intelligence
```

Update `src/firebase/videoService.js` to call the API.

### Option 2: Custom ML Model (Cloud Functions)

Deploy a Cloud Function that:
1. Triggers on video upload
2. Runs your pose estimation model
3. Writes results back to Firestore

### Option 3: Third-party API

Use services like:
- Pose detection APIs
- Movement analysis platforms
- Sports performance APIs

---

## 📱 Testing Locally Before Deploy

```bash
# Run dev server
npm run dev

# Visit http://localhost:5173

# Test video upload feature
# (Will use Firebase backend even in dev mode)
```

---

## 🎯 Next Steps

1. **Get Firebase config** from console
2. **Update** `src/firebase/config.js`
3. **Deploy rules**: `npx firebase deploy --only firestore,storage`
4. **Deploy app**: `npm run deploy`
5. **Add video upload UI** to athlete dashboard
6. **Test** with real video file

---

## 🆘 Troubleshooting

### "Firebase is not configured"
→ Update `src/firebase/config.js` with real values

### "Permission denied" on upload
→ Deploy storage rules: `npx firebase deploy --only storage`

### "Collection not found"
→ Deploy Firestore rules: `npx firebase deploy --only firestore`

### Build fails
→ Make sure Firebase config is valid (no placeholders)

---

## 📚 Documentation

- Architecture: `FIREBASE-ARCHITECTURE.md`
- Original plan: `FIREBASE-DEPLOY.md`
- Subdomain setup: `SUBDOMAIN-SETUP.md`
