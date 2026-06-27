# Firebase Token Renewal & Management Strategy

## Overview
Firebase CI tokens expire every ~90 days. This document outlines an automated renewal strategy with manual backup steps.

## ✅ Recommended: Automated Renewal Reminder

We've set up a **GitHub Actions workflow** (`.github/workflows/firebase-token-renewal.yml`) that:
- Runs monthly on the 1st of every month
- Creates an issue if token renewal is needed
- Sends Slack notification (if configured)
- Provides clear instructions for renewal

**No manual setup needed** - just watch for the GitHub issue!

### Benefits
✅ Automatic monthly checks
✅ Creates tracking issue in GitHub
✅ Slack notifications (optional)
✅ Clear instructions provided
✅ No manual calendar reminders needed

---

## 📋 Manual Renewal (When Needed)

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

