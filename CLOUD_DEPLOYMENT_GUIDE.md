# Video Analysis Tool - Cloud Deployment Guide

## 🎯 Overview

This guide will help you deploy the Video Analysis Tool as a cloud-based service with:
- **Backend API**: Flask API on Google Cloud Run (processes videos)
- **Frontend**: React component integrated into your existing website
- **Storage**: Temporary cloud storage for uploads and results

## 📋 Prerequisites

### Required Tools
1. **Google Cloud SDK** - [Install here](https://cloud.google.com/sdk/docs/install)
2. **Docker** - [Install here](https://docs.docker.com/get-docker/)
3. **Node.js & npm** - Already installed (for your React app)
4. **Google Cloud Project** with billing enabled

### Verify Installation
```powershell
# Check Google Cloud SDK
gcloud version

# Check Docker
docker --version

# Check Node.js
node --version
```

## 🚀 Step-by-Step Deployment

### Step 1: Set Up Google Cloud Project

```powershell
# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create watch-mail-trial --name="Moove Video Analysis"

# Set the project
gcloud config set project watch-mail-trial

# Enable billing
# Go to: https://console.cloud.google.com/billing
```

### Step 2: Configure API Deployment

Edit `deploy-api.ps1` and update:
```powershell
$PROJECT_ID = "watch-mail-trial"  # Your GCP project ID
$SERVICE_NAME = "video-analysis-api"
$REGION = "us-central1"  # Choose closest region
```

### Step 3: Deploy the Backend API

```powershell
# Make sure you're in the project root
cd "c:\Users\Dell 5330\OneDrive\Documents\Moove"

# Run the deployment script
.\deploy-api.ps1
```

This will:
- Enable required Google Cloud APIs
- Build a Docker container with your Python code
- Push it to Google Container Registry
- Deploy to Cloud Run
- Display the service URL (save this!)

**Expected Output:**
```
✅ Deployment Complete!
Service URL: https://video-analysis-api-xyz-uc.a.run.app
```

### Step 4: Configure Frontend

1. Create `.env` file from template:
```powershell
Copy-Item .env.example .env
```

2. Edit `.env` and update the API URL:
```
VITE_API_URL=https://video-analysis-api-xyz-uc.a.run.app
```

3. Install frontend dependencies (if not done):
```powershell
npm install
```

### Step 5: Test the API

```powershell
# Test health endpoint
curl https://your-service-url/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "video-analysis-api",
  "timestamp": "2026-03-26T10:30:00"
}
```

### Step 6: Run Frontend Locally (Testing)

```powershell
# Start development server
npm run dev
```

Navigate to `http://localhost:5173` and:
1. Click "Video Analysis" in the sidebar
2. Upload a test video
3. Process and download results

### Step 7: Deploy Frontend to Firebase

```powershell
# Build production version
npm run build

# Deploy to Firebase Hosting
firebase deploy --only hosting
```

Your app will be live at: `https://watch-mail-trial.web.app`

## 🔧 Configuration Options

### Backend API Configuration

**Memory & CPU** (in `deploy-api.ps1`):
```powershell
--memory 4Gi    # Increase for larger videos
--cpu 2         # Increase for faster processing
```

**Timeout** (max processing time):
```powershell
--timeout 600   # 10 minutes (adjust as needed)
```

**Max Instances** (concurrent requests):
```powershell
--max-instances 10  # Limit to control costs
```

### Frontend Configuration

**Environment Variables** (`.env`):
```
VITE_API_URL=https://your-api-url
```

## 💰 Cost Estimation

### Google Cloud Run (Backend)
- **Free Tier**: 2 million requests/month, 360,000 GB-seconds
- **Typical Cost**: $0.01-0.05 per video processed
- **Monthly (100 videos)**: ~$2-5

### Firebase Hosting (Frontend)
- **Free Tier**: 10GB storage, 360MB/day transfer
- **Typical Cost**: Free for testing, $0.026/GB after

### Total Monthly Cost (Testing Phase)
- Backend: ~$2-5
- Frontend: Free
- **Total: ~$2-5/month**

## 🔒 Security Considerations

### Current Setup (Testing)
- ✅ API is publicly accessible (no auth required)
- ✅ Suitable for functional testing
- ⚠️ **Not recommended for production**

### For Production (Future)
Add authentication:
1. **Firebase Authentication** on frontend
2. **Cloud Run IAM** or API keys
3. **CORS restrictions** to your domain only

## 📊 Monitoring & Logs

### View API Logs
```powershell
# View recent logs
gcloud run services logs read video-analysis-api --region=us-central1

# Follow logs in real-time
gcloud run services logs tail video-analysis-api --region=us-central1
```

### Cloud Console
View metrics: https://console.cloud.google.com/run

## 🐛 Troubleshooting

### Issue: Docker build fails
```powershell
# Solution: Ensure Docker Desktop is running
# Restart Docker and try again
```

### Issue: "Permission denied" during deployment
```powershell
# Solution: Re-authenticate
gcloud auth login
gcloud auth application-default login
```

### Issue: API timeout during processing
```powershell
# Solution: Increase timeout in deploy script
--timeout 900  # 15 minutes
```

### Issue: Frontend can't connect to API
1. Check `.env` file has correct `VITE_API_URL`
2. Verify API is deployed: `curl https://your-api-url/health`
3. Check browser console for CORS errors
4. Rebuild frontend: `npm run build`

### Issue: Video upload fails
- Check file size (max 500MB)
- Check file format (MP4, AVI, MOV, MKV, WEBM)
- Verify API logs: `gcloud run services logs read video-analysis-api`

## 🔄 Updating the Deployment

### Update Backend Code
```powershell
# Make changes to video_annotation_tool.py or api/app.py
# Then redeploy:
.\deploy-api.ps1
```

### Update Frontend Code
```powershell
# Make changes to src/pages/VideoAnalysisTool.jsx
# Then rebuild and redeploy:
npm run build
firebase deploy --only hosting
```

## 📱 Accessing the Tool

### Local Development
```
http://localhost:5173
→ Click "Video Analysis" in sidebar
```

### Production
```
https://watch-mail-trial.web.app
→ Click "Video Analysis" in sidebar
```

## 🎓 API Endpoints Reference

### Upload Video
```
POST /api/upload
Body: multipart/form-data with 'video' file
Returns: { job_id, filename }
```

### Process Video
```
POST /api/process/{job_id}
Returns: { success, files[] }
```

### Get Results
```
GET /api/results/{job_id}
Returns: { files: [{ filename, size, type }] }
```

### Download File
```
GET /api/download/{job_id}/{filename}
Returns: File download
```

### Check Status
```
GET /api/status/{job_id}
Returns: { status: 'uploaded' | 'completed' | 'not_found' }
```

### Cleanup
```
DELETE /api/cleanup/{job_id}
Returns: { success: true }
```

## ✅ Quick Test Checklist

After deployment:
- [ ] API health check responds
- [ ] Frontend loads in browser
- [ ] "Video Analysis" appears in sidebar
- [ ] Can select video file
- [ ] Upload shows progress
- [ ] Processing completes
- [ ] Can download all result files
- [ ] Annotated video plays correctly
- [ ] CSV files open in Excel

## 🎯 Next Steps

1. **Test with real videos** from your use case
2. **Share URL** with team for feedback
3. **Monitor usage** in Cloud Console
4. **Gather requirements** for production features:
   - User authentication
   - Result storage/history
   - Batch processing
   - Email notifications
   - Real-time progress updates

## 📞 Support

### Deployment Issues
- Google Cloud Run docs: https://cloud.google.com/run/docs
- Firebase Hosting docs: https://firebase.google.com/docs/hosting

### Application Issues
- Check the generated documentation:
  - `VIDEO_ANNOTATION_GUIDE.md`
  - `JOINT_ANGLES_REFERENCE.md`

---

**Ready to deploy?** Run these commands:
```powershell
# 1. Deploy backend
.\deploy-api.ps1

# 2. Update .env with API URL
# Edit .env file

# 3. Test locally
npm run dev

# 4. Deploy frontend
npm run build
firebase deploy --only hosting
```

🎉 Your Video Analysis Tool is now live in the cloud!
