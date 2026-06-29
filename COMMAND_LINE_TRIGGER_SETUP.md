# Command-Line Setup for Independent Deployment Triggers

## Issue: Repository Not Connected

Your GitHub repository needs to be connected to Cloud Build first.

---

## Step 1: Connect Repository

Visit this link to authorize and connect Sport_Enable:

```
https://console.cloud.google.com/cloud-build/triggers;region=global/connect?project=watch-mail-trial
```

Or run (if using gcloud with GitHub CLI):
```bash
gcloud source repos clone sport-enable --project=watch-mail-trial
```

---

## Step 2: Create Backend Trigger (After connection)

```bash
gcloud builds triggers create github \
  --name=moove-api-backend \
  --repo-name=Sport_Enable \
  --repo-owner=Maheshgok \
  --branch-pattern=^main$ \
  --build-config=cloudbuild.yaml \
  --included-files="api/**,cloud-run/**,cloudbuild.yaml" \
  --project=watch-mail-trial
```

---

## Step 3: Create Frontend Trigger (After connection)

```bash
gcloud builds triggers create github \
  --name=moove-ui-frontend \
  --repo-name=Sport_Enable \
  --repo-owner=Maheshgok \
  --branch-pattern=^main$ \
  --build-config=cloudbuild-frontend.yaml \
  --included-files="src/**,vite.config.js,package.json,tailwind.config.js,postcss.config.js,index.html" \
  --project=watch-mail-trial
```

---

## Quick Alternative: Use Console UI (2 minutes)

If command line is taking too long, just:

1. Go to: https://console.cloud.google.com/cloud-build/triggers?project=watch-mail-trial
2. Click "Connect Repository"
3. Select "GitHub" → Authorize → Select Sport_Enable
4. Click "Create Trigger" twice (once for backend, once for frontend)
5. Configure as shown in INDEPENDENT_DEPLOYMENT_SETUP.md

---

## Testing After Setup

```bash
# List all triggers
gcloud builds triggers list --project=watch-mail-trial

# Should show:
# - moove-api-backend
# - moove-ui-frontend
```

---

## Full Setup Script (After connection)

```bash
PROJECT_ID=watch-mail-trial
REPO_NAME=Sport_Enable
REPO_OWNER=Maheshgok

# Backend trigger
gcloud builds triggers create github \
  --name=moove-api-backend \
  --repo-name=$REPO_NAME \
  --repo-owner=$REPO_OWNER \
  --branch-pattern=^main$ \
  --build-config=cloudbuild.yaml \
  --included-files="api/**,cloud-run/**,cloudbuild.yaml" \
  --project=$PROJECT_ID

# Frontend trigger
gcloud builds triggers create github \
  --name=moove-ui-frontend \
  --repo-name=$REPO_NAME \
  --repo-owner=$REPO_OWNER \
  --branch-pattern=^main$ \
  --build-config=cloudbuild-frontend.yaml \
  --included-files="src/**,vite.config.js,package.json,tailwind.config.js,postcss.config.js,index.html" \
  --project=$PROJECT_ID

# Verify
gcloud builds triggers list --project=$PROJECT_ID
```

---

## If Still Getting Errors

The most common issue is repository not connected. To fix:

1. **Visit:** https://console.cloud.google.com/cloud-build/triggers?project=watch-mail-trial
2. **Click:** "Connect Repository"
3. **Select:** GitHub account (Maheshgok)
4. **Find:** Sport_Enable
5. **Click:** "Connect"

Then run the gcloud commands above.

---

## Once Connected

After connecting Sport_Enable repo:

```bash
# Re-run the trigger creation
gcloud builds triggers create github \
  --name=moove-api-backend \
  --repo-name=Sport_Enable \
  --repo-owner=Maheshgok \
  --branch-pattern=^main$ \
  --build-config=cloudbuild.yaml \
  --included-files="api/**,cloud-run/**,cloudbuild.yaml" \
  --project=watch-mail-trial
```

Should succeed! ✅
