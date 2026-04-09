# Deploy Moove MVP to GCP (Subdomain)

## Option 1: Cloud Storage + Cloud CDN (Recommended for Static Sites)

### Step 1: Create a Cloud Storage Bucket
```bash
# Replace with your preferred subdomain name
gsutil mb -c STANDARD -l us-central1 gs://moove.edgechurn.ai

# Make bucket publicly readable
gsutil iam ch allUsers:objectViewer gs://moove.edgechurn.ai
```

### Step 2: Configure for Website Hosting
```bash
# Set index and error pages
gsutil web set -m index.html -e index.html gs://moove.edgechurn.ai
```

### Step 3: Upload Production Files
```bash
cd dist
gsutil -m cp -r * gs://moove.edgechurn.ai/
```

### Step 4: Set Cache Control (Optional but Recommended)
```bash
# Cache HTML for 5 minutes (for updates)
gsutil -m setmeta -h "Cache-Control:public, max-age=300" gs://moove.edgechurn.ai/*.html

# Cache static assets for 1 year
gsutil -m setmeta -h "Cache-Control:public, max-age=31536000" gs://moove.edgechurn.ai/assets/*
```

### Step 5: Configure DNS
In your GCP Cloud DNS (or wherever edgechurn.ai DNS is managed):

1. Create a CNAME record:
   - **Name**: `moove` (or `demo`)
   - **Type**: CNAME
   - **Value**: `c.storage.googleapis.com.`

2. Wait 5-10 minutes for DNS propagation

### Step 6: Verify Domain Ownership (One-time)
```bash
# Add a CNAME record for domain verification
# Name: _acme-challenge.moove
# Value: [verification code from GCP Console]
```

---

## Option 2: Using Existing Load Balancer (If you have one for edgechurn.ai)

If edgechurn.ai uses a Cloud Load Balancer, you can add the Moove bucket as a backend:

1. Go to **Cloud Load Balancing** in GCP Console
2. Edit your existing load balancer
3. Add a new backend bucket: `moove.edgechurn.ai`
4. Add a new host rule: `moove.edgechurn.ai` → bucket backend
5. Your SSL certificate should automatically cover `*.edgechurn.ai`

---

## Quick Deployment Script

Create `deploy.sh` (or `deploy.ps1` for Windows):

```bash
#!/bin/bash
# Build production
npm run build

# Upload to GCP
gsutil -m rsync -r -d dist/ gs://moove.edgechurn.ai/

# Invalidate cache if using Cloud CDN
# gcloud compute url-maps invalidate-cdn-cache [LOAD_BALANCER_NAME] --path "/*"

echo "✅ Deployed to https://moove.edgechurn.ai"
```

---

## Testing Locally Before Deploy

```bash
# Serve the built dist folder locally
npx serve dist

# Visit http://localhost:3000
```

---

## Important Notes

1. **Bucket Name**: Must match your subdomain exactly (moove.edgechurn.ai)
2. **DNS**: CNAME from subdomain to `c.storage.googleapis.com.`
3. **SSL**: If using Load Balancer, SSL is automatic. For direct storage access, you'll need Cloud CDN.
4. **SPA Routing**: Since this is a single-page app with no routing library, the current setup works fine. If you add React Router later, you'll need to configure 404 fallback to index.html.

---

## Cost Estimate
- Storage: ~$0.01/month (for 235KB)
- Bandwidth: ~$0.12/GB egress
- Total: Likely < $5/month for moderate traffic
