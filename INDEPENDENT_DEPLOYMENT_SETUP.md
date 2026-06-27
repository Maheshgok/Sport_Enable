# Independent Backend & Frontend Deployment Setup

## Overview

```
Single Git Repository
    ↓
Two Independent Cloud Build Triggers
    ↙                              ↘
cloudbuild.yaml (Backend)    cloudbuild-frontend.yaml
Triggers on:                 Triggers on:
  - api/**                     - src/**
  - cloud-run/**               - vite.config.js
    ↓                          - package.json
Cloud Run (API)              - tailwind.config.js
                               ↓
                            Firebase Hosting (React)
```

---

## Setup Instructions

### Part 1: Create Backend Trigger (API → Cloud Run)

1. **Go to:** Cloud Build Console
   - URL: https://console.cloud.google.com/cloud-build/triggers

2. **Click:** "Create Trigger"

3. **Configure:**
   ```
   Name: moove-api-backend
   Repository: Sport_Enable (GitHub)
   Branch: main
   Build Configuration: Cloud Build (cloudbuild.yaml)
   Location: Repository (cloudbuild.yaml at root)
   ```

4. **Set Path Filter (IMPORTANT - only build when backend changes):**
   - Click "Show Included/Excluded files (optional)"
   - Include files:
     ```
     api/**
     cloud-run/**
     cloudbuild.yaml
     ```

5. **Save Trigger**

**Result:** Backend builds ONLY when `api/` or `cloud-run/` changes ✅

---

### Part 2: Create Frontend Trigger (React → Firebase Hosting)

1. **Go to:** Cloud Build Console
   - URL: https://console.cloud.google.com/cloud-build/triggers

2. **Click:** "Create Trigger"

3. **Configure:**
   ```
   Name: moove-ui-frontend
   Repository: Sport_Enable (GitHub)
   Branch: main
   Build Configuration: Cloud Build (cloudbuild-frontend.yaml)
   Location: Repository (cloudbuild-frontend.yaml at root)
   ```

4. **Set Path Filter (IMPORTANT - only build when frontend changes):**
   - Click "Show Included/Excluded files (optional)"
   - Include files:
     ```
     src/**
     vite.config.js
     package.json
     tailwind.config.js
     postcss.config.js
     index.html
     ```

5. **Save Trigger**

**Result:** Frontend builds ONLY when `src/` or config changes ✅

---

## How It Works

### Scenario 1: Push API Changes Only
```
git commit -am "Fix API error handling"
git push origin main

↓

GCP detects changes to api/app_firestore.py
✅ Backend trigger fires
❌ Frontend trigger does not fire

Result: Only backend rebuilds & redeploys (2 minutes)
Frontend unchanged - no redeploy needed
```

### Scenario 2: Push Frontend Changes Only
```
git commit -am "Update dashboard UI"
git push origin main

↓

GCP detects changes to src/pages/Dashboard.jsx
✅ Frontend trigger fires
❌ Backend trigger does not fire

Result: Only frontend rebuilds & redeploys (5 minutes)
Backend unchanged - no redeploy needed
```

### Scenario 3: Push Both Backend & Frontend
```
git commit -am "Add new feature with UI"
git push origin main

↓

GCP detects changes to both api/ and src/
✅ Backend trigger fires
✅ Frontend trigger fires

Result: Both build in parallel (runs simultaneously)
Backend goes live (~5 min)
Frontend goes live (~5 min)
```

---

## Environment Variables

### Backend (Cloud Run)
No additional setup needed - uses existing Cloud Run env vars:
- FIREBASE_PROJECT_ID
- GCS_BUCKET_NAME
- JWT_SECRET
- DATABASE_URL

### Frontend (Firebase Hosting)
Set in Cloud Build trigger substitutions:
- `_FIREBASE_TOKEN`: Firebase deploy token

**Get Firebase Deploy Token:**
```bash
firebase login:ci

# This generates a token - copy and paste into Cloud Build
```

Then add to Cloud Build trigger:
- Go to Trigger → Edit
- Under "Substitutions" add:
  ```
  _FIREBASE_TOKEN: <your-token-here>
  ```

---

## Deployment Architecture

```
┌──────────────────────────────────────────────────┐
│          Your Git Repository (main)              │
│                                                  │
│  api/              src/                          │
│  cloud-run/        vite.config.js                │
│  cloudbuild.yaml   tailwind.config.js            │
│  cloudbuild-frontend.yaml   package.json         │
└──────────────────────────────────────────────────┘
           ↓                          ↓
    ┌─────────────┐            ┌─────────────┐
    │ Cloud Build │            │ Cloud Build │
    │ (Backend)   │            │ (Frontend)  │
    └─────────────┘            └─────────────┘
           ↓                          ↓
    ┌─────────────┐            ┌──────────────┐
    │ Cloud Run   │            │   Firebase   │
    │   (API)     │            │   Hosting    │
    └─────────────┘            └──────────────┘
```

---

## Testing the Setup

### After triggers are configured:

1. **Make Backend Changes:**
   ```bash
   # Edit api/app_firestore.py
   git add api/
   git commit -m "Update API"
   git push origin main
   
   # Watch: GCP Cloud Build console
   # Should see: moove-api-backend trigger fire
   # Should NOT see: moove-ui-frontend trigger fire
   ```

2. **Make Frontend Changes:**
   ```bash
   # Edit src/pages/Dashboard.jsx
   git add src/
   git commit -m "Update UI"
   git push origin main
   
   # Watch: GCP Cloud Build console
   # Should see: moove-ui-frontend trigger fire
   # Should NOT see: moove-api-backend trigger fire
   ```

3. **Make Both Changes:**
   ```bash
   # Edit both api/ and src/
   git add .
   git commit -m "Feature: New dashboard"
   git push origin main
   
   # Watch: GCP Cloud Build console
   # Should see: Both triggers fire simultaneously
   ```

---

## Monitoring Builds

### Backend (API)
Go to: https://console.cloud.google.com/cloud-build/builds
- Filter: `Build config = cloudbuild.yaml`
- Triggers on: `api/**` or `cloud-run/**` changes
- Deploys to: Cloud Run (asia-south1)

### Frontend (React)
Go to: https://console.cloud.google.com/cloud-build/builds
- Filter: `Build config = cloudbuild-frontend.yaml`
- Triggers on: `src/**` or config changes
- Deploys to: Firebase Hosting

---

## Build Time Estimates

| Build | Time | Why |
|-------|------|-----|
| Backend API | ~8-12 min | Docker build + push + Cloud Run deploy |
| Frontend UI | ~5-8 min | npm install + vite build + hosting deploy |
| Both (parallel) | ~12 min | Runs simultaneously, takes max of both |

---

## Key Benefits of Independent Deployment

✅ **Only deploy what changed**
- Push to api/ → Only backend builds (5 min)
- Push to src/ → Only frontend builds (3 min)
- Push to both → Both build in parallel (5 min)

✅ **Faster feedback loop**
- No waiting for unrelated builds
- Independent rollback if needed

✅ **Less resource usage**
- Only one build system runs at a time
- Save build minutes and costs

✅ **Zero coordination needed**
- Backend team can deploy independently
- Frontend team can deploy independently

✅ **Professional CI/CD**
- Smart path-based triggers
- Enterprise-grade automation
- Complete deployment history

---

## File Summary

```
Root Directory:
├── cloudbuild.yaml              ← Backend (API → Cloud Run)
├── cloudbuild-frontend.yaml     ← Frontend (React → Firebase)
├── api/
│   └── app_firestore.py
├── cloud-run/
│   └── Dockerfile
├── src/
│   ├── pages/
│   ├── components/
│   └── App.jsx
└── package.json
```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Backend trigger fires for frontend changes | No path filter set | Add `includedFiles` to trigger |
| Frontend trigger fires for backend changes | No path filter set | Add `includedFiles` to trigger |
| Firebase deploy fails | Missing deploy token | Get token: `firebase login:ci` |
| Build takes too long | Dependencies downloading | Add `.gcloudignore` file |
| Both triggers fire when only one changed | Path filters incorrect | Review trigger settings |

---

## Next Steps

1. ✅ Commit and push both `cloudbuild.yaml` and `cloudbuild-frontend.yaml`
2. ✅ Create backend trigger in Cloud Build console
3. ✅ Create frontend trigger in Cloud Build console
4. ✅ Set path filters for both triggers
5. ✅ Get Firebase deploy token
6. ✅ Add token to frontend trigger substitutions
7. ✅ Test with small changes to verify triggers fire independently

---

## Summary

You now have:

✅ **Backend Pipeline:** Code → API → Cloud Run (auto)
✅ **Frontend Pipeline:** Code → React → Firebase (auto)
✅ **Independent Triggers:** Each builds only when needed
✅ **Smart Deployment:** No unnecessary builds
✅ **Professional Setup:** Enterprise-grade CI/CD

**Your system is now fully automated!** 🚀

---

**Questions?** Check Cloud Build console logs for detailed info on any build:
https://console.cloud.google.com/cloud-build/builds
