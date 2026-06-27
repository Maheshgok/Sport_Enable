# Frontend GitHub Actions - Fix Firebase Deployment

## Issues Found ❌

1. **Firebase token expired** in GitHub Secrets
2. **firebase.json missing site name** for hosting deployment

---

## Fix Applied ✅

Updated `firebase.json` to include site name:
```json
"hosting": {
  "site": "moove-ui",
  "public": "dist",
  ...
}
```

---

## What You Need to Do (2 minutes)

### Step 1: Generate New Firebase Token

Run this command locally:
```bash
firebase login:ci
```

This will:
- Open your browser for authentication
- Generate a **new deployment token**
- Display the token in terminal

### Step 2: Copy the Token

The output will show:
```
✔ Success! Use this token to login on a CI server:

YOUR_NEW_TOKEN_HERE
```

**Copy the entire token** (starts with a long random string)

### Step 3: Update GitHub Actions Secret

1. Go to: https://github.com/Maheshgok/Sport_Enable/settings/secrets/actions
2. Click **"New repository secret"**
3. Name: `FIREBASE_TOKEN`
4. Value: Paste the token from step 2
5. Click **"Add secret"**

### Step 4: Rerun GitHub Actions

1. Go to: https://github.com/Maheshgok/Sport_Enable/actions
2. Find the failed "Deploy to Firebase Hosting" workflow
3. Click **"Re-run all jobs"**
4. Watch it deploy! ✅

---

## Quick Checklist

- [ ] Run `firebase login:ci` locally
- [ ] Copy new token
- [ ] Update GitHub Secret `FIREBASE_TOKEN`
- [ ] Rerun GitHub Actions workflow
- [ ] Verify frontend deploys to Firebase Hosting

---

## After Deployment

Your system will have:
- ✅ Backend API live on Cloud Run
- ✅ Frontend React app live on Firebase Hosting
- ✅ Both auto-deploy on push to main

---

## Firebase Token Security Note

⚠️ The token is sensitive - treat it like a password:
- ✅ Store in GitHub Secrets (encrypted)
- ❌ Never commit to git
- ❌ Never share in messages/docs

---

## Need Help?

If you run into issues:
1. Check GitHub Actions logs: https://github.com/Maheshgok/Sport_Enable/actions
2. Verify token was pasted correctly (no spaces/quotes)
3. Re-run the workflow after updating the secret

Ready to regenerate the token? Let me know when done! 🚀
