# Quick Start - Video Analysis Tool

## 🚀 Deploy in 5 Minutes

### 1. Prerequisites
```powershell
# Verify tools are installed
gcloud version
docker --version
node --version
```

### 2. Deploy Backend
```powershell
# Set your project ID
$PROJECT_ID = "watch-mail-trial"

# Login and deploy
gcloud auth login
.\deploy-api.ps1
```

**Save the service URL from output!**

### 3. Configure Frontend
```powershell
# Create .env file
Copy-Item .env.example .env

# Edit .env and add your API URL:
# VITE_API_URL=https://your-service-url-here
```

### 4. Test Locally
```powershell
npm run dev
# Visit http://localhost:5173
# Click "Video Analysis" in sidebar
```

### 5. Deploy Frontend
```powershell
npm run build
firebase deploy --only hosting
```

## ✅ Done!

Access your tool at: `https://watch-mail-trial.web.app`

---

## 📖 Full Documentation

For detailed instructions, see:
- [CLOUD_DEPLOYMENT_GUIDE.md](CLOUD_DEPLOYMENT_GUIDE.md) - Complete deployment guide
- [VIDEO_ANNOTATION_GUIDE.md](VIDEO_ANNOTATION_GUIDE.md) - Tool usage documentation
- [JOINT_ANGLES_REFERENCE.md](JOINT_ANGLES_REFERENCE.md) - Understanding results

## 🎯 What You Built

✅ **Flask API** running on Google Cloud Run  
✅ **React Frontend** integrated into your website  
✅ **Processes videos** to analyze human movement  
✅ **Exports CSV files** with joint angles and metrics  
✅ **Generates annotated videos** with pose overlay

## 🧪 Test Workflow

1. Upload a video (MP4, AVI, MOV, etc.)
2. Click "Process Video"
3. Wait 1-5 minutes (depending on video length)
4. Download results:
   - Annotated video
   - CSV data files
   - Analysis report

## 💰 Costs

**Testing Phase**: ~$2-5/month  
**Free Tier**: First 2 million API requests free

## 🔧 Common Issues

**Issue**: API not responding  
**Fix**: Check `.env` has correct `VITE_API_URL`

**Issue**: Upload fails  
**Fix**: Video must be < 500MB

**Issue**: Docker build fails  
**Fix**: Ensure Docker Desktop is running

## 📞 Need Help?

Check the full guide: [CLOUD_DEPLOYMENT_GUIDE.md](CLOUD_DEPLOYMENT_GUIDE.md)
