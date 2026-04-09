# Video Analysis Tool - README

## 🎯 Overview

A cloud-based video analysis tool that uses Google MediaPipe to analyze human movement in videos. Integrated into your Moove platform for functional testing.

## 🚀 Quick Start

### Deploy to Cloud (5 Minutes)

```powershell
# 1. Deploy backend API
.\deploy-api.ps1

# 2. Configure frontend
Copy-Item .env.example .env
# Edit .env with your API URL

# 3. Test locally
npm run dev

# 4. Deploy to production
npm run build
firebase deploy --only hosting
```

**Full guide**: [QUICKSTART_DEPLOYMENT.md](QUICKSTART_DEPLOYMENT.md)

## 📁 Project Structure

```
Moove/
├── api/
│   ├── app.py                    # Flask REST API
│   └── requirements.txt          # Python dependencies
├── src/
│   ├── pages/
│   │   └── VideoAnalysisTool.jsx # React component
│   ├── components/
│   │   └── layout/
│   │       └── Sidebar.jsx       # Updated navigation
│   └── App.jsx                   # Updated routing
├── video_annotation_tool.py      # Core analysis engine
├── Dockerfile                    # Container config
├── deploy-api.ps1                # Deployment script
├── .env.example                  # Environment template
└── Documentation/
    ├── QUICKSTART_DEPLOYMENT.md
    ├── CLOUD_DEPLOYMENT_GUIDE.md
    ├── VIDEO_ANNOTATION_GUIDE.md
    ├── JOINT_ANGLES_REFERENCE.md
    └── DEPLOYMENT_SUMMARY.md
```

## 🎨 Features

### Video Analysis
- ✅ Upload videos up to 500MB
- ✅ Supports MP4, AVI, MOV, MKV, WEBM
- ✅ Real-time processing status
- ✅ Progress tracking during upload

### Movement Tracking
- ✅ 14 joint angles (knees, elbows, hips, shoulders, ankles, wrists, neck)
- ✅ Frame-by-frame coordinate data
- ✅ Movement velocity analysis
- ✅ Range of motion calculations
- ✅ Left/right symmetry analysis

### Output Files
- ✅ Annotated video with pose overlay
- ✅ CSV files with complete data
- ✅ Min/Max angle analysis
- ✅ Human-readable summary report

## 🖥️ User Interface

Access via sidebar: **Video Analysis** → Upload → Process → Download

### Workflow
1. Click "Video Analysis" in sidebar
2. Select video file (drag-drop or click)
3. Click "Upload Video"
4. Click "Process Video"
5. Wait for completion (1-5 min)
6. Download result files

## 🔧 Technology Stack

### Backend
- **Python 3.10** - Core language
- **Flask** - REST API framework
- **MediaPipe** - Pose estimation
- **OpenCV** - Video processing
- **NumPy/Pandas** - Data analysis
- **Google Cloud Run** - Hosting platform

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Lucide Icons** - Icons
- **Firebase Hosting** - Static hosting

## 📊 What Gets Analyzed

### Body Landmarks (18 points)
- Head: nose, eyes, ears
- Upper body: shoulders, elbows, wrists
- Lower body: hips, knees, ankles

### Calculated Metrics (14 angles)
- **Knees**: Hip-Knee-Ankle angle
- **Elbows**: Shoulder-Elbow-Wrist angle
- **Hips**: Shoulder-Hip-Knee angle
- **Shoulders**: Hip-Shoulder-Elbow angle
- **Ankles**: Knee-Ankle-Vertical angle
- **Wrists**: Elbow-Wrist-Forward angle
- **Neck**: Head position angle

### Data Outputs
- Min/Max angles with timestamps
- Range of motion for each joint
- Movement velocity per joint
- Frame-by-frame coordinates
- Statistical analysis

## 💰 Cost

### Testing Phase
- **Backend**: ~$2-5/month (Google Cloud Run)
- **Frontend**: FREE (Firebase Hosting free tier)
- **Total**: ~$2-5/month

### Per Video
- Small (< 1 min): ~$0.01
- Medium (1-5 min): ~$0.02-0.03
- Large (5-10 min): ~$0.04-0.05

## 🔒 Security

### Current (Testing)
- API is publicly accessible
- No authentication required
- Temporary file storage only

### Recommended for Production
- Add Firebase Authentication
- Implement API keys/JWT
- Add rate limiting
- Persistent storage with access control

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [QUICKSTART_DEPLOYMENT.md](QUICKSTART_DEPLOYMENT.md) | 5-minute quick start |
| [CLOUD_DEPLOYMENT_GUIDE.md](CLOUD_DEPLOYMENT_GUIDE.md) | Complete deployment guide |
| [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) | Architecture overview |
| [VIDEO_ANNOTATION_GUIDE.md](VIDEO_ANNOTATION_GUIDE.md) | How to use the tool |
| [JOINT_ANGLES_REFERENCE.md](JOINT_ANGLES_REFERENCE.md) | Understanding results |

## 🧪 Testing

### Test API Connection
```powershell
.\test-api.ps1
```

### Test Locally Before Deploy
```powershell
# Terminal 1: Start backend
cd api
python app.py

# Terminal 2: Start frontend
npm run dev
```

### Verify Deployment
```powershell
# Check backend
curl https://your-api-url/health

# Check frontend
# Visit: https://watch-mail-trial.web.app
```

## 🐛 Troubleshooting

### API Not Responding
1. Check `.env` has correct `VITE_API_URL`
2. Verify API is deployed: `gcloud run services list`
3. Check logs: `gcloud run services logs read video-analysis-api`

### Upload Fails
1. Check file size (< 500MB)
2. Verify file format (MP4, AVI, MOV, MKV, WEBM)
3. Check browser console for errors

### Processing Timeout
1. Video may be too long (> 10 min)
2. Increase timeout in `deploy-api.ps1`
3. Split video into shorter segments

### Docker Build Fails
1. Ensure Docker Desktop is running
2. Restart Docker and try again
3. Check Dockerfile for errors

## 📞 Support

### Deployment Issues
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [Firebase Docs](https://firebase.google.com/docs)

### Application Issues
- Check API logs for errors
- Review documentation
- Test with smaller videos first

## 🎓 Use Cases

### Athletic Training
- Analyze squat depth and form
- Track running gait patterns
- Monitor jump mechanics
- Compare left/right symmetry

### Physical Therapy
- Measure range of motion
- Track recovery progress
- Verify exercise compliance
- Document patient improvements

### Biomechanics Research
- Extract movement data for analysis
- Compare movement patterns
- Study joint kinematics
- Export to research tools

## 🔄 Updates & Maintenance

### Update Backend
```powershell
# Make changes to code
# Redeploy
.\deploy-api.ps1
```

### Update Frontend
```powershell
# Make changes to React components
npm run build
firebase deploy --only hosting
```

### Monitor Usage
```
https://console.cloud.google.com/run
```

## ✅ Success Checklist

After deployment:
- [ ] API health endpoint responds
- [ ] Frontend loads without errors
- [ ] Can access "Video Analysis" in sidebar
- [ ] Video upload works
- [ ] Processing completes successfully
- [ ] All files downloadable
- [ ] CSV files open correctly
- [ ] Annotated video plays

## 🚀 Next Steps

1. **Test**: Upload sample videos
2. **Gather Feedback**: Share with team
3. **Iterate**: Based on user feedback
4. **Plan Production**: Authentication, storage, etc.

## 📄 License

This tool uses:
- MediaPipe (Apache License 2.0)
- OpenCV (Apache License 2.0)

---

## 🎉 Ready to Start?

```powershell
# Deploy now!
.\deploy-api.ps1
```

For detailed instructions, see [QUICKSTART_DEPLOYMENT.md](QUICKSTART_DEPLOYMENT.md)
