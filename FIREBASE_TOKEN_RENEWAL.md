# Firebase Token Renewal & Management Strategy

## Overview
Firebase CI tokens expire every ~90 days. This document outlines an automated renewal strategy with manual backup steps.

## ✅ Recommended: Smart Multi-Channel Notifications

We've set up **advanced GitHub Actions workflows** with buffer times:

### Workflow 1: Basic Monthly Check (Simple)
- **File**: `.github/workflows/firebase-token-renewal.yml`
- **Runs**: 1st of every month
- **Alerts**: GitHub issue + optional Slack
- **Best for**: Small teams with basic needs

### Workflow 2: Smart Buffer-Based Alerts (Recommended)
- **File**: `.github/workflows/firebase-token-smart-renewal.yml`
- **Runs**: 1st and 15th of every month
- **Calculates**: Days remaining before expiry
- **Alert Levels**:
  - ✅ **OK** (0-60 days): Silent, no action
  - ℹ️ **INFO** (60-75 days): GitHub issue created
  - ⚠️ **WARNING** (75-85 days): Slack + GitHub issue
  - 🚨 **CRITICAL** (85+ days): **Email + Slack + GitHub issue**
- **Best for**: Production teams wanting maximum visibility

### Setup: Multi-Channel Notifications

#### Option A: Email Alerts (Recommended for Critical)
1. **Enable Email** (optional, for CRITICAL alerts only):
   - Go: https://github.com/Maheshgok/Sport_Enable/settings/secrets/actions
   - Add secret: `EMAIL_USERNAME` = your Gmail
   - Add secret: `EMAIL_PASSWORD` = [Gmail app password](https://myaccount.google.com/apppasswords)
   - Add secret: `ALERT_EMAIL` = your-email@edgechurn.ai

#### Option B: Slack Notifications
1. **Create Slack Webhook**:
   - Go: https://api.slack.com/messaging/webhooks
   - Create new app → "Create New App" → "From scratch"
   - Name: "Firebase Alerts"
   - Add to workspace
   - Enable "Incoming Webhooks"
   - Click "Add New Webhook to Workspace"
   - Copy webhook URL

2. **Add to GitHub Secrets**:
   - Go: https://github.com/Maheshgok/Sport_Enable/settings/secrets/actions
   - New secret: `SLACK_WEBHOOK_URL` = (paste webhook)

#### Option C: GitHub Issues (Built-in - No Setup)
- Automatic ✅
- No configuration needed
- Issues tracked in GitHub Projects

### Benefits
✅ Multiple notification channels (GitHub + Slack + Email)
✅ Buffer-based alerts (60/75/85 day marks)
✅ Automatic expiration date calculation
✅ CRITICAL alerts only via email (not spam)
✅ Works completely automatically
✅ No manual calendar reminders

---

## � Advanced: Google Cloud Scheduler (Zero Maintenance)

**For completely automated renewal without manual intervention:**

This uses Google Cloud Scheduler + Cloud Functions to auto-generate tokens.

### Requirements
- GCP project access
- Enable Cloud Scheduler + Cloud Functions APIs
- Service account with appropriate permissions

### Implementation
1. Create Cloud Function that runs `firebase login:ci` programmatically
2. Schedule it to run every 75 days
3. Function commits new token to GitHub automatically
4. No manual intervention ever needed

**Status**: Can be implemented if you want zero-manual-touch solution. Currently blocked by organization policy on service account keys, but this approach bypasses that limitation.

---

## 📱 Option 4: External Services (IFTTT / Zapier)

**For integrations with tools you already use:**

### Setup (IFTTT Example)
1. Go: https://ifttt.com
2. Create applet: "If GitHub issue created with label 'firebase' then send email"
3. Connect GitHub + Email services
4. Receive email whenever renewal issue is created

### Benefits
✅ Works with your existing email/Slack/Teams
✅ Centralized notifications
✅ Integrates with calendars and reminders



If the automated workflow alerts you or the deployment fails with auth error:

### Step 1: Generate New Token Locally
```bash
firebase login:ci --project=watch-mail-trial --no-localhost
```

This will:
1. Open auth.firebase.tools in browser
2. Prompt you to authorize with Google
3. Provide an authorization code
4. Print a new token to terminal

**Copy the token** from the terminal output.

### Step 2: Update GitHub Secret

Go to: `https://github.com/Maheshgok/Sport_Enable/settings/secrets/actions`

1. Click **FIREBASE_TOKEN** secret
2. Click **Update**
3. Paste new token in **Secret** field
4. Click **Save**

### Step 3: Verify Deployment Works
- Go to: `https://github.com/Maheshgok/Sport_Enable/actions`
- Find "Deploy to Firebase Hosting" workflow
- Click **Run workflow** → **Run workflow**
- Wait for ✅ success

---

## 🔐 Alternative: Service Account (Zero Maintenance)

**Status**: Attempted but disabled by GCP policy
**Recommendation**: Contact GCP admin to disable `constraints/iam.disableServiceAccountKeyCreation` on the project

If enabled, we could use:
```yaml
env:
  GOOGLE_APPLICATION_CREDENTIALS: ${{ runner.temp }}/firebase-sa-key.json

steps:
  - name: Setup Service Account
    run: |
      echo "${{ secrets.FIREBASE_SERVICE_ACCOUNT }}" | base64 -d > ${{ runner.temp }}/firebase-sa-key.json
      
  - name: Deploy
    run: firebase deploy --only hosting --project watch-mail-trial
```

**Benefits**: Zero expiration, no renewal needed ever.

---

## 🚨 Quick Reference

| Issue | Solution | Time |
|-------|----------|------|
| Deployment fails: "credentials are no longer valid" | Run token renewal steps above | 5 min |
| GitHub issue created: "Firebase Token Renewal Required" | Follow instructions in issue | 5 min |
| Want zero-maintenance solution | Request GCP admin enable service account keys | 1 email |

---

## 📅 Timeline & Reminders

- **Day 1-75**: Token is valid ✅
- **Day 76**: Monthly check workflow runs, may alert if approaching expiry
- **Day 85-90**: GitHub issue created if needed
- **Day 90+**: Deployment will fail → Manual renewal required

---

## 🔔 Slack Integration (Optional)

To enable Slack notifications when renewal is needed:

1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Add to GitHub Secrets: `SLACK_WEBHOOK_URL`
3. Workflow will now send Slack messages

---

## ✨ Current Token Info

- **Project**: watch-mail-trial
- **Service**: Firebase Hosting
- **Last Generated**: 2026-06-27
- **Expires**: ~2026-09-27 (90 days)
- **Status**: ✅ Active

