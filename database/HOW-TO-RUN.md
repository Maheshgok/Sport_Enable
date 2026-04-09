# Quick Setup - Run Database Migrations

## 🚀 Easiest Method: Google Cloud Console (5 minutes)

**No installation required!** Use Cloud Shell with built-in PostgreSQL client.

### Step 1: Open Cloud Console
Click this link: [Open Cloud SQL Instance](https://console.cloud.google.com/sql/instances/moove-db/overview?project=watch-mail-trial)

### Step 2: Open Cloud Shell
- Click the **Cloud Shell icon** (>_) in the top-right corner of the console
- Wait for Cloud Shell to initialize (takes ~10 seconds)

### Step 3: Upload SQL Files
In Cloud Shell terminal, run:
```bash
# Create working directory
mkdir -p moove-db-setup/schema

# You'll need to upload the SQL files. Click the ⋮ (three dots) menu in Cloud Shell
# Select "Upload" and upload these files:
# - init.sql
# - schema/01_users_and_profiles.sql
# - schema/02_relationships.sql
# - schema/03_clinical_data.sql
# - schema/04_access_control.sql
# - schema/05_sample_data.sql
```

**OR** use Cloud Shell Editor to create the files:
```bash
# Open editor
cloudshell edit moove-db-setup/init.sql

# Copy-paste content from: database/init.sql
# Save with Ctrl+S

# Repeat for all schema files
```

### Step 4: Run Migrations
```bash
cd moove-db-setup

# Connect to database and run init.sql
gcloud sql connect moove-db --user=postgres --database=moove_production < init.sql

# Password: MooveSecure2026!

# Run schema files in order
gcloud sql connect moove-db --user=postgres --database=moove_production < schema/01_users_and_profiles.sql
gcloud sql connect moove-db --user=postgres --database=moove_production < schema/02_relationships.sql
gcloud sql connect moove-db --user=postgres --database=moove_production < schema/03_clinical_data.sql
gcloud sql connect moove-db --user=postgres --database=moove_production < schema/04_access_control.sql
gcloud sql connect moove-db --user=postgres --database=moove_production < schema/05_sample_data.sql
```

### Step 5: Verify Setup
```bash
# Connect interactively
gcloud sql connect moove-db --user=postgres --database=moove_production

# Inside psql, run:
\dt physio_app.*

# Should show 17 tables

# Check sample data:
SELECT * FROM physio_app.v_active_care_teams;

# Exit:
\q
```

---

## 💻 Alternative: Install PostgreSQL Client Locally

If you prefer to run migrations from your local machine:

### Windows Installation

#### Option A: Official Installer (Recommended)
1. Download from: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
2. Choose PostgreSQL 14 or higher
3. During installation:
   - ✅ Keep "Command Line Tools"
   - ❌ Uncheck "PostgreSQL Server" (not needed)
   - ❌ Uncheck "Stack Builder" (not needed)
4. Restart PowerShell
5. Run: `.\database\run-migrations.ps1`

#### Option B: Chocolatey (if you have it)
```powershell
choco install postgresql -y
refreshenv
.\database\run-migrations.ps1
```

### After Installation
```powershell
# Navigate to database folder
cd "C:\Users\Dell 5330\OneDrive\Documents\Moove\database"

# Run migration helper script
.\run-migrations.ps1

# Or run manually:
$env:PGPASSWORD="MooveSecure2026!"
psql -h 34.93.206.105 -U postgres -d moove_production -f init.sql
psql -h 34.93.206.105 -U postgres -d moove_production -f schema/01_users_and_profiles.sql
# ... etc
```

---

## 🖥️ Alternative: GUI Tool (DBeaver)

If you prefer a graphical interface:

1. **Download DBeaver**: https://dbeaver.io/download/
2. **Install** (community edition is free)
3. **Create Connection**:
   - Click "New Database Connection"
   - Select "PostgreSQL"
   - Enter details:
     ```
     Host: 34.93.206.105
     Port: 5432
     Database: moove_production
     Username: postgres
     Password: MooveSecure2026!
     ```
   - Test connection
4. **Run Scripts**:
   - Right-click on connection → SQL Editor → Open SQL Script
   - Open `init.sql` and execute
   - Repeat for all schema files in order
5. **Verify**:
   - Expand physio_app schema in database navigator
   - Should see 17 tables

---

## ✅ Verification Checklist

After running migrations, verify:

```sql
-- 1. Check all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'physio_app'
ORDER BY table_name;

-- Should return 17 tables:
-- assessments, athlete_profiles, athlete_teams, audit_log,
-- caretaker_profiles, clinical_notes, coach_profiles, 
-- daily_tasks, exercise_assignments, exercise_library,
-- exercise_sessions, physiotherapist_profiles,
-- progress_milestones, users

-- 2. Check sample data loaded
SELECT COUNT(*) FROM physio_app.users;
-- Should return: 4

SELECT COUNT(*) FROM physio_app.athlete_teams;
-- Should return: 1

SELECT COUNT(*) FROM physio_app.exercise_library;
-- Should return: 5

-- 3. Test access control function
SELECT physio_app.can_access_athlete(
  'p1111111-1111-1111-1111-111111111111'::UUID,
  'aa111111-1111-1111-1111-111111111111'::UUID
);
-- Should return: true

-- 4. View active care team
SELECT * FROM physio_app.v_active_care_teams;
-- Should return 1 row with Sarah Johnson's care team
```

---

## 🎯 Next Steps After Successful Setup

1. ✅ Database schema created
2. ✅ Sample data loaded
3. ⏳ Build backend API (Node.js + Express + PostgreSQL)
4. ⏳ Connect frontend to backend
5. ⏳ Implement authentication (JWT)
6. ⏳ Add video upload functionality

---

## 🆘 Troubleshooting

### "Connection refused" error
- Verify your IP is still authorized: `gcloud sql instances describe moove-db`
- Your IP may have changed (dynamic IP) - re-run the authorized networks command

### "FATAL: password authentication failed"
- Password: `MooveSecure2026!`
- Ensure no extra spaces when copying

### "extension vector does not exist"
- Comment out vector columns in SQL files (lines with `vector(512)`)
- pgvector may not be available on db-f1-micro tier
- Use JSONB as fallback for embeddings

### "permission denied for schema physio_app"
- Ensure you're connecting as `postgres` user
- Check: `\dn` to list schemas
- Run: `SET search_path TO physio_app;`

---

**Recommended**: Use Cloud Console method - it's fastest and requires no installation!
