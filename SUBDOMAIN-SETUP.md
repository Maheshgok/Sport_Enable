# Setting Up moove.edgechurn.ai Subdomain

## Step 1: Add Custom Domain in Firebase Console

1. Go to: https://console.firebase.google.com/project/watch-mail-trial/hosting/sites
2. Click **"Add custom domain"**
3. Enter: `moove.edgechurn.ai` (or your preferred subdomain)
4. Click **"Continue"**

Firebase will show you DNS records to add. Keep this page open!

---

## Step 2: Add DNS Records in GCP Cloud DNS

### Option A: Using GCP Console (Recommended)

1. Go to **Cloud DNS**: https://console.cloud.google.com/net-services/dns/zones
2. Select your DNS zone for **edgechurn.ai**
3. Click **"Add Record Set"**

### Records to Add:

**Record 1: TXT (Domain Verification)**
- **DNS Name**: `moove` (or your subdomain)
- **Resource Record Type**: TXT
- **TTL**: 300
- **TXT Data**: (Copy from Firebase Console - looks like `google-site-verification=...`)

**Record 2 & 3: A Records (Firebase Hosting IPs)**

Add these two A records (Firebase provides these IPs):

- **DNS Name**: `moove`
- **Resource Record Type**: A
- **TTL**: 300
- **IPv4 Address**: 
  - First record: (IP from Firebase, usually similar to `151.101.1.195`)
  - Second record: (IP from Firebase, usually similar to `151.101.65.195`)

---

### Option B: Using gcloud CLI

```powershell
# Set your project
gcloud config set project YOUR_GCP_PROJECT_ID

# Get your DNS zone name
gcloud dns managed-zones list

# Add TXT record for verification
gcloud dns record-sets create moove.edgechurn.ai. --zone=edgechurn-ai-zone --type=TXT --ttl=300 --rrdatas="google-site-verification=YOUR_VERIFICATION_CODE"

# Add A records (replace with IPs from Firebase)
gcloud dns record-sets create moove.edgechurn.ai. --zone=edgechurn-ai-zone --type=A --ttl=300 --rrdatas="151.101.1.195,151.101.65.195"
```

**Note**: Replace `edgechurn-ai-zone` with your actual DNS zone name.

---

## Step 3: Verify in Firebase

1. Go back to Firebase Console
2. Click **"Verify"** (may take 5-15 minutes for DNS propagation)
3. Once verified, Firebase will:
   - Provision SSL certificate (takes 5-30 minutes)
   - Set up HTTPS redirect
   - Deploy your site to the custom domain

---

## Step 4: Check Status

**DNS Propagation Check:**
```powershell
# Check if DNS is working
nslookup moove.edgechurn.ai

# Or detailed check
Resolve-DnsName moove.edgechurn.ai -Type A
```

**Expected Output:**
```
Name:    moove.edgechurn.ai
Addresses:  151.101.1.195
            151.101.65.195
```

---

## Troubleshooting

### DNS not propagating?
- Wait 10-15 minutes
- Clear DNS cache: `ipconfig /flushdns`
- Check if records exist: `gcloud dns record-sets list --zone=YOUR_ZONE`

### SSL Certificate pending?
- Normal - takes 15-30 minutes
- Check status in Firebase Console → Hosting → Custom domains

### Wrong IP addresses?
- Use exact IPs provided by Firebase (they may differ from examples above)
- Firebase uses different IPs for different regions

---

## Final Result

Once complete, your Moove MVP will be accessible at:
- **https://moove.edgechurn.ai** (custom domain)
- **https://watch-mail-trial.web.app** (Firebase default domain)

Both URLs will work with automatic HTTPS and SSL certificates!

---

## Alternative Subdomains

If you prefer different naming:
- `demo.edgechurn.ai` - Demo-focused
- `app.edgechurn.ai` - Generic app
- `recovery.edgechurn.ai` - Product-specific

Just use the same DNS setup process with your chosen subdomain.
