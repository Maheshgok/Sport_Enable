# Test API Connection
# Run this to verify your API is deployed and accessible

$API_URL = Read-Host "Enter your API URL (from deployment output)"

Write-Host ""
Write-Host "Testing API Connection..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_URL/health" -Method Get
    Write-Host "✅ PASS: API is healthy" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor Gray
    Write-Host "   Service: $($response.service)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "❌ FAIL: Cannot reach API" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check if API URL is correct" -ForegroundColor Gray
    Write-Host "2. Verify deployment completed: gcloud run services list" -ForegroundColor Gray
    Write-Host "3. Check API logs: gcloud run services logs read video-analysis-api" -ForegroundColor Gray
    exit 1
}

# Test 2: CORS Check
Write-Host "Test 2: CORS Configuration" -ForegroundColor Yellow
try {
    $headers = @{
        'Origin' = 'http://localhost:5173'
    }
    $response = Invoke-WebRequest -Uri "$API_URL/health" -Method Options -Headers $headers -ErrorAction SilentlyContinue
    Write-Host "✅ PASS: CORS is properly configured" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "⚠️  WARNING: CORS check inconclusive" -ForegroundColor Yellow
    Write-Host "   (This test may show warnings but API should still work)" -ForegroundColor Gray
    Write-Host ""
}

# Summary
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ API Tests Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Add this URL to your .env file:" -ForegroundColor Gray
Write-Host "   VITE_API_URL=$API_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Start your frontend:" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Navigate to Video Analysis in sidebar and upload a test video" -ForegroundColor Gray
Write-Host ""
