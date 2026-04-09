# Deploy Video Analysis API to Google Cloud Run
# Using Cloud Run's source deployment (no local Docker needed!)

$PROJECT_ID = "watch-mail-trial"
$SERVICE_NAME = "video-analysis-api"
$REGION = "asia-south1"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deploying Video Analysis API (From Source)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Project: $PROJECT_ID"
Write-Host "Service: $SERVICE_NAME"
Write-Host "Region: $REGION"
Write-Host ""

# Set the project
Write-Host "Setting GCP project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

# Enable required APIs
Write-Host ""
Write-Host "Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable storage.googleapis.com

# Create GCS bucket for video storage
$BUCKET_NAME = "$PROJECT_ID-video-analysis"
Write-Host ""
Write-Host "Creating/verifying GCS bucket: $BUCKET_NAME" -ForegroundColor Yellow
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Bucket created successfully" -ForegroundColor Green
} else {
    Write-Host "[INFO] Bucket already exists or creation skipped" -ForegroundColor Gray
}

# Deploy from source (Google Cloud Build handles everything!)
Write-Host ""
Write-Host "Deploying to Cloud Run from source..." -ForegroundColor Yellow
Write-Host "(Google Cloud Build will build the container for you)" -ForegroundColor Gray
Write-Host ""

gcloud run deploy $SERVICE_NAME `
  --source . `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --memory 4Gi `
  --cpu 2 `
  --timeout 600 `
  --max-instances 10 `
  --port 8080 `
  --set-env-vars "GCS_BUCKET_NAME=$BUCKET_NAME"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Cloud Run deployment failed!" -ForegroundColor Red
    exit 1
}

# Get the service URL
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "[SUCCESS] Deployment Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Service URL: " -NoNewline
Write-Host "$SERVICE_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Test API: " -NoNewline -ForegroundColor Yellow
Write-Host "curl $SERVICE_URL/health" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Update .env file with:" -ForegroundColor Yellow
Write-Host "   VITE_API_URL=$SERVICE_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Deploy frontend:" -ForegroundColor Yellow
Write-Host "   npm run build" -ForegroundColor Gray
Write-Host "   firebase deploy --only hosting" -ForegroundColor Gray
Write-Host ""
