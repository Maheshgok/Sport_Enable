# Firebase Deployment Guide for Moove MVP

## Quick Setup & Deploy

### Step 1: Login to Firebase
```powershell
npx firebase login
```

### Step 2: Link to Your Firebase Project

**Option A: Use existing edgechurn.ai project**
```powershell
# List your projects
npx firebase projects:list

# Link to your project (replace with your project ID)
npx firebase use YOUR_PROJECT_ID
```

**Option B: Create new project for Moove**
```powershell
npx firebase projects:create moove-mvp
npx firebase use moove-mvp
```

### Step 3: Deploy
```powershell
# Build and deploy in one command
npm run build
npx firebase deploy --only hosting
```

---

## Setting Up Subdomain (moove.edgechurn.ai)

After first deployment, configure custom domain:

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Go to **Hosting** → **Add custom domain**
4. Enter: `moove.edgechurn.ai`
5. Follow DNS verification steps (add TXT record)
6. Add the provided DNS records:
   - Type: A
   - Host: moove
   - Value: (provided by Firebase)

Firebase will automatically provision SSL certificate.

---

## Multiple Sites in One Project (Recommended)

If you want both edgechurn.ai and moove.edgechurn.ai in the same Firebase project:

1. Create a new site:
```powershell
npx firebase hosting:sites:create moove-mvp
```

2. Update `.firebaserc`:
```json
{
  "projects": {
    "default": "YOUR_PROJECT_ID"
  },
  "targets": {
    "YOUR_PROJECT_ID": {
      "hosting": {
        "moove": ["moove-mvp"]
      }
    }
  }
}
```

3. Update `firebase.json`:
```json
{
  "hosting": {
    "target": "moove",
    "public": "dist",
    ...
  }
}
```

4. Deploy to specific site:
```powershell
npm run build
npx firebase deploy --only hosting:moove
```

---

## Easy Deploy Script

Add to `package.json`:
```json
"scripts": {
  "deploy": "npm run build && firebase deploy --only hosting",
  "deploy:preview": "npm run build && firebase hosting:channel:deploy preview"
}
```

Then just run:
```powershell
npm run deploy
```

---

## Preview Channel (Test Before Production)

```powershell
npm run build
npx firebase hosting:channel:deploy preview
```

This creates a temporary URL like:
`https://YOUR_PROJECT--preview-RANDOM.web.app`

---

## Rollback if Needed

```powershell
npx firebase hosting:rollback
```
