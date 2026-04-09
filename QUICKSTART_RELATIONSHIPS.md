# Moove - Relationship Management System
## Quick Start Guide

---

## System Overview

**Moove** is a sports performance platform with a controlled relationship management system where:

1. **Athletes** select their sport during registration
2. **Coaches** and **Parents/Guardians** connect via invite-accept mechanism
3. **All relationship changes** require super admin approval via email
4. **No direct modifications** - all changes are gated by admin review

---

## Architecture

### User Types & Roles

| Role | Description | Special Requirements | Can Send Invites? |
|------|-------------|---------------------|-------------------|
| **Athlete** | Sports performers | Must select sport & position | ✅ Yes (coaches, parents, physios) |
| **Coach** | Train athletes | Optional specialization | ✅ Yes (athletes, parents, physios, coaches) |
| **Physiotherapist** | Medical professionals | Optional license number | ✅ Yes (athletes, coaches) |
| **Parent/Guardian/Manager** | Legal guardians/managers | Must specify guardian type | ❌ **NO - Can ONLY accept** |
| **Caretaker** | Support staff | General access | ✅ Yes (limited) |
| **Admin/Super User** | System administrators | Approve all relationship changes | ✅ Yes (anyone) |

### Key Tables

```
users
├── athlete_profiles (sport_id, position)
├── coach_profiles (specialization)
├── physiotherapist_profiles (license_number)
└── parent_guardian_profiles (guardian_type, permissions)

relationship_invitations (pending invites with tokens)
relationship_change_requests (pending admin approval)
relationships (active connections)
relationship_audit_log (complete history)
```

---

## Installation

### 1. Prerequisites

- PostgreSQL 14+
- Python 3.9+
- Node.js 16+ (for frontend)

### 2. Database Setup

```powershell
# Set environment variable for database
$env:DATABASE_URL = "postgresql://postgres:password@localhost:5432/moove_db"

# Create database
psql -U postgres -c "CREATE DATABASE moove_db;"

# Run base schema
cd database
psql -U postgres -d moove_db -f schema/01_users_and_profiles.sql
psql -U postgres -d moove_db -f schema/02_relationships.sql
psql -U postgres -d moove_db -f schema/03_clinical_data.sql
psql -U postgres -d moove_db -f schema/04_access_control.sql

# Run relationship management schema (NEW)
psql -U postgres -d moove_db -f schema/07_relationships.sql

# Verify tables were created
psql -U postgres -d moove_db -c "\dt physio_app.*"
```

Expected output should include:
- `users`
- `athlete_profiles`
- `coach_profiles`
- `physiotherapist_profiles`
- `parent_guardian_profiles` ✨ NEW
- `relationship_invitations` ✨ NEW
- `relationship_change_requests` ✨ NEW
- `relationships` ✨ NEW
- `relationship_audit_log` ✨ NEW

### 3. Backend Setup

```powershell
# Navigate to API directory
cd api

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file
@"
DATABASE_URL=postgresql://postgres:password@localhost:5432/moove_db
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_EXPIRATION_HOURS=24

# Email configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@moove.com

# App configuration
APP_BASE_URL=http://localhost:3000

# GCS configuration (optional for video storage)
GCS_BUCKET_NAME=moove-videos
"@ | Out-File -FilePath .env -Encoding utf8

# Test database connection
python -c "from db import test_connection; test_connection()"
```

### 4. Create Super Admin

```powershell
# Run super user creation script
python create_super_user.py

# Follow prompts:
# Email: admin@moove.com
# Password: [secure password]
# First Name: Admin
# Last Name: User
```

### 5. Start Backend Server

```powershell
python app.py
```

Server runs on `http://localhost:8080`

### 6. Frontend Setup

```powershell
# Navigate to project root
cd ..

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on `http://localhost:3000`

---

## Usage Examples

### 1. Register as Athlete

```bash
POST http://localhost:8080/api/auth/register
Content-Type: application/json

{
  "email": "athlete@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "roles": ["athlete"],
  "sport_id": "football-uuid",        ← Required for athlete
  "position": "Forward"                ← Optional
}
```

Response:
```json
{
  "success": true,
  "token": "eyJ...",
  "user": {
    "user_id": "uuid",
    "email": "athlete@example.com",
    "roles": ["athlete"],
    "athlete_profile": {
      "athlete_id": "uuid",
      "sport_id": "football-uuid",
      "position": "Forward"
    }
  }
}
```

### 2. Register as Parent/Guardian

```bash
POST http://localhost:8080/api/auth/register
Content-Type: application/json

{
  "email": "parent@example.com",
  "password": "SecurePass123!",
  "first_name": "Jane",
  "last_name": "Doe",
  "roles": ["parent"],
  "guardian_type": "parent",           ← Required for parent role
  "relationship_to_athlete": "Mother"  ← Optional
}
```

**⚠️ Important:** Parents can ONLY accept invitations. They cannot send invitations.

### 3. Register as Coach

```bash
POST http://localhost:8080/api/auth/register
Content-Type: application/json

{
  "email": "coach@example.com",
  "password": "SecurePass123!",
  "first_name": "Mike",
  "last_name": "Johnson",
  "roles": ["coach"],
  "specialization": "Football - Youth Development",  ← Optional
  "years_of_experience": 10                          ← Optional
}
```

**What Coaches Can Do:**
- ✅ Invite athletes, parents, physiotherapists, other coaches
- ✅ View videos and reports of connected athletes
- ✅ Prescribe training plans

### 4. Register as Physiotherapist

```bash
POST http://localhost:8080/api/auth/register
Content-Type: application/json

{
  "email": "physio@example.com",
  "password": "SecurePass123!",
  "first_name": "Dr. Sarah",
  "last_name": "Williams",
  "roles": ["physiotherapist"],
  "specialization": "Sports Medicine",   ← Optional
  "license_number": "PT-12345"           ← Optional
}
```

**What Physiotherapists Can Do:**
- ✅ Invite athletes and coaches
- ✅ View medical data of connected athletes
- ✅ Prescribe specific analyses

---

### 5. Coach Invites Athlete

```bash
POST http://localhost:8080/api/invitations/send
Authorization: Bearer <coach-token>
Content-Type: application/json

{
  "invitee_email": "athlete@example.com",
  "relationship_type": "coach_athlete",
  "coach_id": "coach-profile-uuid",
  "athlete_id": "athlete-profile-uuid",
  "message": "Hi! I'd like to work with you."
}
```

Response:
```json
{
  "success": true,
  "invitation_id": "uuid",
  "expires_at": "2026-04-15T...",
  "message": "Invitation sent successfully"
}
```

Email sent to: `athlete@example.com`

### 4. Athlete Views Invitations

```bash
GET http://localhost:8080/api/invitations/received
Authorization: Bearer <athlete-token>
```

Response:
```json
{
  "success": true,
  "invitations": [
    {
      "invitation_id": "uuid",
      "relationship_type": "coach_athlete",
      "message": "Hi! I'd like to work with you.",
      "inviter": {
        "name": "Coach Mike",
        "email": "coach@example.com"
      },
      "token": "secure-token-xyz",
      "expires_at": "2026-04-15T..."
    }
  ],
  "count": 1
}
```

### 5. Athlete Accepts Invitation

```bash
POST http://localhost:8080/api/invitations/<token>/accept
Authorization: Bearer <athlete-token>
Content-Type: application/json

{
  "response_message": "Looking forward to working together!"
}
```

Response:
```json
{
  "success": true,
  "message": "Invitation accepted. Pending admin approval.",
  "request_id": "uuid"
}
```

Email sent to: **All super admins**

### 6. Admin Reviews Pending Requests

```bash
GET http://localhost:8080/api/admin/relationship-requests
Authorization: Bearer <admin-token>
```

Response:
```json
{
  "success": true,
  "requests": [
    {
      "request_id": "uuid",
      "request_type": "add_relationship",
      "relationship_type": "coach_athlete",
      "requester": {
        "name": "John Doe",
        "email": "athlete@example.com"
      },
      "users": {
        "user_a": "Coach Mike",
        "user_b": "John Doe"
      },
      "reason": "Accepted invitation from ...",
      "priority": "normal",
      "created_at": "2026-04-08T..."
    }
  ],
  "count": 1
}
```

### 7. Admin Approves Request

```bash
POST http://localhost:8080/api/admin/relationship-requests/<request_id>/approve
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "admin_notes": "Verified coach credentials. Approved."
}
```

Response:
```json
{
  "success": true,
  "message": "Relationship created: uuid"
}
```

Emails sent to:
- Coach: "Your relationship with John Doe has been approved"
- Athlete: "Your relationship with Coach Mike has been approved"

### 8. View Active Relationships

```bash
GET http://localhost:8080/api/relationships/mine
Authorization: Bearer <athlete-token>
```

Response:
```json
{
  "success": true,
  "relationships": [
    {
      "relationship_id": "uuid",
      "relationship_type": "coach_athlete",
      "other_user": {
        "user_id": "uuid",
        "name": "Coach Mike",
        "email": "coach@example.com"
      },
      "status": "active",
      "created_at": "2026-04-08T..."
    }
  ],
  "count": 1
}
```

---

## Admin Features

### Approve Request

```bash
POST /api/admin/relationship-requests/{request_id}/approve
Authorization: Bearer <admin-token>
{
  "admin_notes": "Optional notes"
}
```

### Reject Request

```bash
POST /api/admin/relationship-requests/{request_id}/reject
Authorization: Bearer <admin-token>
{
  "rejection_reason": "Required reason",
  "admin_notes": "Optional additional notes"
}
```

### View All Relationships

```bash
GET /api/admin/relationships
Authorization: Bearer <admin-token>
```

### View Audit Log

```bash
GET /api/admin/audit-log
Authorization: Bearer <admin-token>
```

---

## Email Configuration

### Using Gmail

1. Enable 2-Factor Authentication on your Google account
2. Generate App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

3. Update `.env`:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=noreply@moove.com
```

### Using SendGrid

```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_DEFAULT_SENDER=noreply@moove.com
```

---

## Testing

### Run All Tests

```powershell
# Backend tests
cd api
pytest tests/

# Frontend tests
cd ..
npm test
```

### Manual Testing Script

```powershell
# test_relationships.ps1

# 1. Create test admin
$admin = Invoke-RestMethod -Uri "http://localhost:8080/api/auth/register" -Method POST -Body (@{
  email = "admin@test.com"
  password = "Admin123!"
  first_name = "Admin"
  last_name = "User"
  roles = @("admin", "super_user")
} | ConvertTo-Json) -ContentType "application/json"

Write-Host "✓ Admin created: $($admin.user.email)"

# 2. Create test coach
$coach = Invoke-RestMethod -Uri "http://localhost:8080/api/auth/register" -Method POST -Body (@{
  email = "coach@test.com"
  password = "Coach123!"
  first_name = "Coach"
  last_name = "Mike"
  roles = @("coach")
} | ConvertTo-Json) -ContentType "application/json"

Write-Host "✓ Coach created: $($coach.user.email)"

# 3. Create test athlete
$athlete = Invoke-RestMethod -Uri "http://localhost:8080/api/auth/register" -Method POST -Body (@{
  email = "athlete@test.com"
  password = "Athlete123!"
  first_name = "John"
  last_name = "Doe"
  roles = @("athlete")
  sport_id = "football-uuid"
  position = "Forward"
} | ConvertTo-Json) -ContentType "application/json"

Write-Host "✓ Athlete created: $($athlete.user.email)"

# 4. Coach sends invitation
$headers = @{ "Authorization" = "Bearer $($coach.token)" }
$invitation = Invoke-RestMethod -Uri "http://localhost:8080/api/invitations/send" -Method POST -Headers $headers -Body (@{
  invitee_email = "athlete@test.com"
  relationship_type = "coach_athlete"
  message = "Test invitation"
} | ConvertTo-Json) -ContentType "application/json"

Write-Host "✓ Invitation sent: $($invitation.invitation_id)"

# 5. Athlete accepts
$headers = @{ "Authorization" = "Bearer $($athlete.token)" }
$invitations = Invoke-RestMethod -Uri "http://localhost:8080/api/invitations/received" -Headers $headers
$token = $invitations.invitations[0].token
$accept = Invoke-RestMethod -Uri "http://localhost:8080/api/invitations/$token/accept" -Method POST -Headers $headers

Write-Host "✓ Invitation accepted. Request ID: $($accept.request_id)"

# 6. Admin approves
$headers = @{ "Authorization" = "Bearer $($admin.token)" }
$requests = Invoke-RestMethod -Uri "http://localhost:8080/api/admin/relationship-requests" -Headers $headers
$requestId = $requests.requests[0].request_id
$approve = Invoke-RestMethod -Uri "http://localhost:8080/api/admin/relationship-requests/$requestId/approve" -Method POST -Headers $headers -Body (@{
  admin_notes = "Test approval"
} | ConvertTo-Json) -ContentType "application/json"

Write-Host "✓ Request approved"

# 7. Verify relationship
$headers = @{ "Authorization" = "Bearer $($athlete.token)" }
$relationships = Invoke-RestMethod -Uri "http://localhost:8080/api/relationships/mine" -Headers $headers

Write-Host "✓ Relationship verified: $($relationships.relationships[0].relationship_id)"
Write-Host "`nAll tests passed! ✨"
```

---

## Troubleshooting

### Database Connection Issues

```powershell
# Test database connection
python -c "from db import test_connection; test_connection()"

# Check if tables exist
psql -U postgres -d moove_db -c "\dt physio_app.*"

# Check PostgreSQL is running
Get-Service | Where-Object {$_.Name -like "*postgresql*"}
```

### Email Not Sending

```powershell
# Test email configuration
python -c "
from flask import Flask
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

mail = Mail(app)

with app.app_context():
    msg = Message('Test', recipients=['test@example.com'], body='Test')
    mail.send(msg)
    print('Email sent successfully!')
"
```

### Port Already in Use

```powershell
# Kill process on port 8080
$process = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($process) {
    Stop-Process -Id $process.OwningProcess -Force
}

# Or use different port
$env:PORT = "8081"
python app.py
```

---

## Production Deployment

### Environment Variables

```env
# Production settings
DATABASE_URL=postgresql://user:pass@host:5432/dbname
JWT_SECRET_KEY=<strong-random-key>
JWT_EXPIRATION_HOURS=24

# Email (use production SMTP)
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=<sendgrid-api-key>

# App URL
APP_BASE_URL=https://app.moove.com

# Security
FLASK_ENV=production
DEBUG=False
```

### Deploy to Cloud Run

```powershell
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/moove-api
gcloud run deploy moove-api `
  --image gcr.io/PROJECT_ID/moove-api `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars DATABASE_URL=$env:DATABASE_URL,JWT_SECRET_KEY=$env:JWT_SECRET_KEY
```

---

## Next Steps

1. ✅ Run database migration: `psql -U postgres -d moove_db -f database/schema/07_relationships.sql`
2. ✅ Install dependencies: `pip install -r api/requirements.txt`
3. ✅ Create super admin: `python create_super_user.py`
4. ✅ Configure email in `.env`
5. ✅ Start backend: `python app.py`
6. ✅ Test API endpoints with Postman or curl
7. ✅ Implement frontend components (see RELATIONSHIP_IMPLEMENTATION_GUIDE.md)
8. ✅ Deploy to production

---

## Documentation

- **System Design:** `RELATIONSHIP_SYSTEM_DESIGN.md`
- **Implementation Guide:** `RELATIONSHIP_IMPLEMENTATION_GUIDE.md`
- **API Documentation:** `AUTH_API_GUIDE.md`
- **Sport Analysis:** `SPORT_SPECIFIC_ARCHITECTURE.md`

---

## Support

For issues or questions:
- Check troubleshooting section above
- Review implementation guides
- Check audit log for relationship history
- Verify database schema is up to date

---

**System ready! 🚀** All relationship changes are now gated by admin approval for maximum control and security.
