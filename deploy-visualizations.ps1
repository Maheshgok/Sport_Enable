# Quick Deployment Script for Visualization Features
# Deploys backend (Cloud Run) and frontend (Firebase Hosting)

Write-Host "🚀 Deploying Video Analysis Tool with Visualization Features" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Gray

# Check we're in the right directory
if (-not (Test-Path "video_annotation_tool.py")) {
    Write-Host "❌ Error: video_annotation_tool.py not found. Run this from project root." -ForegroundColor Red
    exit 1
}

# 1. Build and deploy backend
Write-Host "`n📦 Step 1: Deploying Backend to Cloud Run..." -ForegroundColor Yellow
Write-Host "Building Docker image..." -ForegroundColor Gray

$buildResult = gcloud builds submit --tag gcr.io/watch-mail-trial/video-analysis-api 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker image built successfully" -ForegroundColor Green
    
    Write-Host "`nDeploying to Cloud Run..." -ForegroundColor Gray
    $deployResult = gcloud run deploy video-analysis-api `
        --image gcr.io/watch-mail-trial/video-analysis-api `
        --platform managed `
        --region asia-south1 `
        --memory 4Gi `
        --cpu 2 `
        --timeout 600 `
        --allow-unauthenticated 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Backend deployed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend deployment failed" -ForegroundColor Red
        Write-Host $deployResult -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    Write-Host $buildResult -ForegroundColor Red
    exit 1
}

# 2. Build and deploy frontend
Write-Host "`n🎨 Step 2: Deploying Frontend to Firebase..." -ForegroundColor Yellow
Write-Host "Building React app..." -ForegroundColor Gray

npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Frontend built successfully" -ForegroundColor Green
    
    Write-Host "`nDeploying to Firebase Hosting..." -ForegroundColor Gray
    firebase deploy --only hosting
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Frontend deployed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend deployment failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Frontend build failed" -ForegroundColor Red
    exit 1
}

# 3. Summary
Write-Host "`n" + ("=" * 70) -ForegroundColor Gray
Write-Host "✅ DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Gray
Write-Host ""
Write-Host "📊 New Features Deployed:" -ForegroundColor Cyan
Write-Host "  • Joint angle visualizations (anterior/posterior views)" -ForegroundColor White
Write-Host "  • Range of motion comparison charts" -ForegroundColor White
Write-Host "  • Movement reversal detection plots" -ForegroundColor White
Write-Host "  • Gait cycle analysis (running biomechanics)" -ForegroundColor White
Write-Host "  • Stride & foot strike analysis" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Access your application:" -ForegroundColor Cyan
Write-Host "  Frontend: https://watch-mail-trial.web.app" -ForegroundColor White
Write-Host "  Backend:  https://video-analysis-api-812016027146.asia-south1.run.app" -ForegroundColor White
Write-Host ""
Write-Host "📝 Test the new features:" -ForegroundColor Cyan
Write-Host "  1. Upload a video with athlete height" -ForegroundColor White
Write-Host "  2. Wait for processing to complete" -ForegroundColor White
Write-Host "  3. Scroll down to see 'Graphical Analysis & Visualizations' section" -ForegroundColor White
Write-Host "  4. View inline images and download high-res versions" -ForegroundColor White
Write-Host ""
Write-Host "📊 Expected Output Files (per analysis):" -ForegroundColor Cyan
Write-Host "  • annotated_video_*.mp4 (with pose overlay)" -ForegroundColor White
Write-Host "  • joint_angles_view_*.png (NEW - 6 joint pairs)" -ForegroundColor Green
Write-Host "  • range_of_motion_*.png (NEW - ROM comparison)" -ForegroundColor Green
Write-Host "  • movement_reversals_*.png (NEW - direction changes)" -ForegroundColor Green
Write-Host "  • gait_analysis_*.png (NEW - running biomechanics)" -ForegroundColor Green
Write-Host "  • stride_analysis_*.png (NEW - foot strike patterns)" -ForegroundColor Green
Write-Host "  • frame_data_*.csv (raw data)" -ForegroundColor White
Write-Host "  • joint_angles_minmax_*.csv (angle extremes)" -ForegroundColor White
Write-Host "  • joint_movements_*.csv (distance traveled)" -ForegroundColor White
Write-Host "  • summary_report_*.txt (text summary)" -ForegroundColor White
Write-Host "  • analytics_*.json (NEW - structured API data)" -ForegroundColor Green
Write-Host ""
Write-Host "🔍 Monitoring:" -ForegroundColor Cyan
Write-Host "  Cloud Run logs: gcloud run logs read video-analysis-api --region asia-south1" -ForegroundColor White
Write-Host "  Check for: '✓ Generated X visualization files'" -ForegroundColor White
Write-Host ""
