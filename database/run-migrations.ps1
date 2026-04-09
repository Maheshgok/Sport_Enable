# PostgreSQL Migration Helper Script
# This script helps run the database migrations

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Moove Database Migration Helper" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if psql is available
$psqlCommand = Get-Command psql -ErrorAction SilentlyContinue

if ($null -eq $psqlCommand) {
    Write-Host "❌ PostgreSQL client (psql) is NOT installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please choose one of these options:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Option 1: Install PostgreSQL (Recommended)" -ForegroundColor Green
    Write-Host "  1. Download from: https://www.postgresql.org/download/windows/" -ForegroundColor White
    Write-Host "  2. Run the installer" -ForegroundColor White
    Write-Host "  3. You can uncheck 'PostgreSQL Server' - we only need command line tools" -ForegroundColor White
    Write-Host "  4. After installation, restart PowerShell and run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 2: Use Google Cloud Console (No installation needed)" -ForegroundColor Green
    Write-Host "  1. Open: https://console.cloud.google.com/sql/instances/moove-db/overview?project=watch-mail-trial" -ForegroundColor White
    Write-Host "  2. Click 'Connect using Cloud Shell' button" -ForegroundColor White
    Write-Host "  3. Run command: gcloud sql connect moove-db --user=postgres --quiet" -ForegroundColor White
    Write-Host "  4. Enter password: MooveSecure2026!" -ForegroundColor White
    Write-Host "  5. Copy and paste SQL commands from the files in database/ folder" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 3: Use DBeaver (GUI Tool)" -ForegroundColor Green
    Write-Host "  1. Download from: https://dbeaver.io/download/" -ForegroundColor White
    Write-Host "  2. Install and create new PostgreSQL connection:" -ForegroundColor White
    Write-Host "     Host: 34.93.206.105" -ForegroundColor White
    Write-Host "     Port: 5432" -ForegroundColor White
    Write-Host "     Database: moove_production" -ForegroundColor White
    Write-Host "     Username: postgres" -ForegroundColor White
    Write-Host "     Password: MooveSecure2026!" -ForegroundColor White
    Write-Host "  3. Open and execute SQL files in order" -ForegroundColor White
    Write-Host ""
    
    exit 1
}

Write-Host "✅ PostgreSQL client found!" -ForegroundColor Green
Write-Host ""

# Set connection details
$DB_HOST = "34.93.206.105"
$DB_PORT = "5432"
$DB_NAME = "moove_production"
$DB_USER = "postgres"
$DB_PASSWORD = "MooveSecure2026!"

Write-Host "Connection Details:" -ForegroundColor Cyan
Write-Host "  Host: $DB_HOST" -ForegroundColor White
Write-Host "  Database: $DB_NAME" -ForegroundColor White
Write-Host "  User: $DB_USER" -ForegroundColor White
Write-Host ""

# Set password environment variable
$env:PGPASSWORD = $DB_PASSWORD

# Change to database directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "Running migrations..." -ForegroundColor Yellow
Write-Host ""

# Array of SQL files to run in order
$sqlFiles = @(
    "init.sql",
    "schema/01_users_and_profiles.sql",
    "schema/02_relationships.sql",
    "schema/03_clinical_data.sql",
    "schema/04_access_control.sql",
    "schema/05_sample_data.sql"
)

$successCount = 0
$failCount = 0

foreach ($file in $sqlFiles) {
    if (Test-Path $file) {
        Write-Host "📄 Running: $file" -ForegroundColor Cyan
        
        try {
            $result = psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f $file 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✅ Success" -ForegroundColor Green
                $successCount++
            } else {
                Write-Host "  ❌ Failed" -ForegroundColor Red
                Write-Host "  Error: $result" -ForegroundColor Red
                $failCount++
            }
        } catch {
            Write-Host "  ❌ Error: $_" -ForegroundColor Red
            $failCount++
        }
        
        Write-Host ""
    } else {
        Write-Host "  ⚠️  File not found: $file" -ForegroundColor Yellow
        $failCount++
        Write-Host ""
    }
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Migration Summary" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ Successful: $successCount" -ForegroundColor Green
Write-Host "❌ Failed: $failCount" -ForegroundColor Red
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "🎉 All migrations completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Verify tables were created" -ForegroundColor White
    Write-Host "  2. Build your backend API" -ForegroundColor White
    Write-Host "  3. Connect frontend to database" -ForegroundColor White
} else {
    Write-Host "⚠️  Some migrations failed. Check errors above." -ForegroundColor Yellow
    Write-Host "You may need to manually run failed migrations." -ForegroundColor Yellow
}

Write-Host ""

# Clear password from environment
$env:PGPASSWORD = ""
