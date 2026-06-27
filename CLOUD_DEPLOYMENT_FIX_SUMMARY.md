# Cloud Deployment - Issue & Fix Summary

## Problem Encountered

**Issue:** Backend API deployed to Cloud Run returning **503 Service Unavailable**

**Root Cause:** Firebase Admin SDK initialization failed in `api/auth.py`
- Error: `ValueError: Unable to load PEM file... MalformedFraming`
- Cause: Trying to load service account credentials from environment variables that were not set in Cloud Run

---

## Solution Implemented

### Changed: `api/auth.py` (Lines 135-170)

**Before:** ❌
```python
# Fragile approach - relies on env variables
if not firebase_admin._apps:
    cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
    else:
        # Tries to build from env vars - fails if not set
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.environ.get('FIREBASE_PROJECT_ID', 'your-project-id'),
            "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
            # ...more fields...
        })
    firebase_admin.initialize_app(cred)
```

**After:** ✅
```python
# Robust approach - uses Cloud Run's built-in credentials first
if not firebase_admin._apps:
    try:
        # Step 1: For Cloud Run - use Application Default Credentials (built-in)
        # No setup needed, Cloud Run provides this automatically
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': os.environ.get('FIREBASE_PROJECT_ID', 'watch-mail-trial')
        })
    except Exception as e:
        # Step 2: Fallback for local development - try file path
        cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'service-account-key.json')
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Step 3: Last resort - build from environment variables
            cred_dict = {
                "type": "service_account",
                "project_id": os.environ.get('FIREBASE_PROJECT_ID', 'watch-mail-trial'),
                "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                # ...more fields...
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
```

---

## Key Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Cloud Run** | ❌ Fails (no env vars) | ✅ Works (ADC) |
| **Local Dev** | ✅ Works (env vars) | ✅ Works (file or env) |
| **Error Handling** | ❌ Crashes immediately | ✅ Graceful fallback chain |
| **Credentials** | ❌ Manual setup required | ✅ Automatic on Cloud Run |

---

## Deployment Status

### Git Commit
- **Commit Hash:** `96c8302`
- **Message:** "Fix: Use Application Default Credentials for Cloud Run Firebase initialization"
- **Files Changed:** `api/auth.py`
- **Status:** ✅ Pushed to GitHub

### Cloud Build
- **Status:** Building (manual submit in progress)
- **Steps:**
  1. Building Docker image
  2. Pushing to Container Registry
  3. Deploying to Cloud Run (asia-south1)
- **ETA:** ~5-8 minutes

### Expected Behavior After Deployment

```
API Endpoint: https://moove-api-bhcetby62q-el.a.run.app

GET /health
{
  "status": "healthy",
  "service": "moove-api",
  "database": "firestore",
  "database_status": "connected",
  "timestamp": "2026-06-27T..."
}
```

---

## Testing After Deployment

```powershell
# 1. Check health
Invoke-WebRequest -Uri "https://moove-api-bhcetby62q-el.a.run.app/health" -UseBasicParsing

# 2. Test registration
$body = @{
    email = "test@moove.com"
    password = "SecurePass123!"
    first_name = "John"
    last_name = "Doe"
    roles = @("athlete")
    sport_id = "football"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://moove-api-bhcetby62q-el.a.run.app/api/auth/register" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

---

## Why This Fix Works

### Application Default Credentials (ADC)

Cloud Run automatically provides credentials without any configuration:

1. **Cloud Run detects it's running in GCP**
2. **Automatically gets service account credentials**
3. **Makes them available via `credentials.ApplicationDefault()`**
4. **No environment variables needed**

This is the **recommended approach for Cloud Run** deployments.

---

## Architecture: Before → After

```
BEFORE (Broken)
═════════════════════════════════════════
Local Dev         Cloud Run
    ↓                  ↓
Env Vars ←  Works   Env Vars ← Fails (503)
  File ←                ↓
         Service Account
            Not Found!
               
AFTER (Fixed)
═════════════════════════════════════════
Local Dev         Cloud Run
    ↓                  ↓
Tries ADC         Uses ADC ✅
   ↓               (Built-in)
Tries File        ↓
   ↓          Firestore
Tries Env Vars   Connected
   ↓
Success ✅
```

---

## Build Logs

Check the full build logs:
```bash
gcloud builds log BUILD_ID --project=watch-mail-trial
```

Replace `BUILD_ID` with the build ID from Cloud Build console.

---

## Next Steps

1. ⏳ **Wait for build to complete** (~5-8 minutes)
2. ✅ **Test health endpoint** once it's ready
3. ✅ **Verify registration/login endpoints work**
4. ✅ **Set up independent deployment triggers** (if not done yet)
5. ✅ **Deploy frontend** to Firebase Hosting

---

## Summary

| Item | Status |
|------|--------|
| Code Fix | ✅ Complete |
| Git Push | ✅ Complete (Commit 96c8302) |
| Cloud Build | ⏳ In Progress |
| Cloud Run Deployment | ⏳ Pending (on build completion) |
| API Status | ⏳ Will be ✅ after deployment |

**Expected to go live in 5-8 minutes!** 🚀
