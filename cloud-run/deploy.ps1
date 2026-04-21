# Deploy Protocol Analysis Service to Cloud Run

param(
    [string]$ProjectId = "your-gcp-project-id",
    [string]$ServiceName = "protocol-analysis-service",
    [string]$Region = "asia-south1"
)

Write-Host "Deploying Protocol Analysis Service to Cloud Run..." -ForegroundColor Green

# Build and deploy to Cloud Run
gcloud run deploy $ServiceName `
    --source . `
    --platform managed `
    --region $Region `
    --project $ProjectId `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --max-instances 10 `
    --timeout 900 `
    --concurrency 1

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment successful!" -ForegroundColor Green

    # Get the service URL
    $serviceUrl = gcloud run services describe $ServiceName `
        --platform managed `
        --region $Region `
        --project $ProjectId `
        --format "value(status.url)"

    Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan

    # Update the API with the service URL
    Write-Host "Update your API configuration with this service URL for Cloud Run jobs." -ForegroundColor Yellow
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}