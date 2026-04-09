# Moove MVP - GCP Deployment Script
# Deploy to subdomain of edgechurn.ai

param(
    [string]$bucketName = "moove.edgechurn.ai",
    [switch]$build = $false
)

Write-Host "🚀 Deploying Moove MVP to GCP..." -ForegroundColor Cyan

# Build if requested
if ($build) {
    Write-Host "📦 Building production bundle..." -ForegroundColor Yellow
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed!" -ForegroundColor Red
        exit 1
    }
}

# Check if dist folder exists
if (-not (Test-Path "dist")) {
    Write-Host "❌ dist folder not found. Run with -build flag." -ForegroundColor Red
    exit 1
}

# Check if gsutil is available
try {
    gsutil version | Out-Null
} catch {
    Write-Host "❌ gsutil not found. Install Google Cloud SDK first." -ForegroundColor Red
    Write-Host "   Download from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

Write-Host "📤 Uploading files to gs://$bucketName..." -ForegroundColor Yellow

# Upload files (excluding source maps for security)
gsutil -m rsync -r -d -x ".*.map$" dist/ "gs://$bucketName/"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Upload failed!" -ForegroundColor Red
    exit 1
}

# Set cache headers
Write-Host "⚙️  Setting cache headers..." -ForegroundColor Yellow

# HTML files - short cache (5 minutes)
gsutil -m setmeta -h "Cache-Control:public, max-age=300" "gs://$bucketName/*.html"

# Assets - long cache (1 year, Vite uses content hashing)
gsutil -m setmeta -h "Cache-Control:public, max-age=31536000, immutable" "gs://$bucketName/assets/*"

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Your app should be available at: https://$bucketName" -ForegroundColor Cyan
Write-Host "" 
Write-Host "Note: DNS propagation may take 5-10 minutes if this is first deployment." -ForegroundColor Yellow
