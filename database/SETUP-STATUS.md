# Database Setup Status

## ✅ Completed

### Cloud SQL Instance
- **Instance Name**: moove-db
- **Region**: asia-south1 (Mumbai)
- **Status**: RUNNABLE ✅
- **Database Version**: PostgreSQL 14
- **Tier**: db-f1-micro (development)
- **Public IP**: 34.93.206.105
- **Project**: watch-mail-trial

### Database
- **Database Name**: moove_production ✅
- **Root User**: postgres
- **Root Password**: MooveSecure2026!

### Network Access
- **Authorized IP**: 114.143.234.6 (your current IP) ✅
- **Connection Ready**: Yes ✅

### Schema Files Created
All SQL migration files are ready in `database/` folder:
- ✅ init.sql - Extensions and schema
- ✅ schema/01_users_and_profiles.sql - User tables
- ✅ schema/02_relationships.sql - Team assignments
- ✅ schema/03_clinical_data.sql - Clinical data
- ✅ schema/04_access_control.sql - Security
- ✅ schema/05_sample_data.sql - Test data
- ✅ run_all.sql - Master script

## ⏳ Next Step: Run Schema Scripts

You need to run the SQL scripts to create tables. Choose one method:

### Method 1: Using PostgreSQL Client (psql) - Recommended

#### Install PostgreSQL Client for Windows
```powershell
# Option A: Using Chocolatey (if installed)
choco install postgresql

# Option B: Download installer from
# https://www.postgresql.org/download/windows/
# Choose "PostgreSQL" installer, install only the "Command Line Tools"
```

#### Run Migrations
```powershell
# Navigate to database folder
cd "C:\Users\Dell 5330\OneDrive\Documents\Moove\database"

# Set password environment variable (no prompt needed)
$env:PGPASSWORD="MooveSecure2026!"

# Run all migrations
psql -h 34.93.206.105 -U postgres -d moove_production -f run_all.sql

# Or run individually
psql -h 34.93.206.105 -U postgres -d moove_production -f init.sql
psql -h 34.93.206.105 -U postgres -d moove_production -f schema/01_users_and_profiles.sql
psql -h 34.93.206.105 -U postgres -d moove_production -f schema/02_relationships.sql
psql -h 34.93.206.105 -U postgres -d moove_production -f schema/03_clinical_data.sql
psql -h 34.93.206.105 -U postgres -d moove_production -f schema/04_access_control.sql
psql -h 34.93.206.105 -U postgres -d moove_production -f schema/05_sample_data.sql
```

### Method 2: Using Google Cloud Console

1. Go to [Cloud SQL Instances](https://console.cloud.google.com/sql/instances)
2. Click on `moove-db`
3. Click "Connect using Cloud Shell"
4. In Cloud Shell, run:
```bash
gcloud sql connect moove-db --user=postgres --quiet
# Enter password: MooveSecure2026!

# Copy-paste each SQL file content manually
# Or upload files to Cloud Shell and run:
\i run_all.sql
```

### Method 3: Using DBeaver/pgAdmin (GUI Tools)

1. Download [DBeaver](https://dbeaver.io/download/) or [pgAdmin](https://www.pgadmin.org/download/)
2. Create new PostgreSQL connection:
   - **Host**: 34.93.206.105
   - **Port**: 5432
   - **Database**: moove_production
   - **Username**: postgres
   - **Password**: MooveSecure2026!
3. Open and execute SQL files in order

## 📊 Database Schema Overview

Once scripts are run, you'll have:

### Core Tables (9 tables)
- users
- athlete_profiles
- physiotherapist_profiles
- coach_profiles
- caretaker_profiles
- athlete_teams

### Clinical Tables (8 tables)
- assessments
- exercise_library
- exercise_assignments
- exercise_sessions
- daily_tasks
- progress_milestones
- clinical_notes
- audit_log

### Views (2 views)
- v_active_care_teams
- v_professional_workloads

### Functions (5 functions)
- update_updated_at_column()
- update_professional_caseloads()
- get_user_profile_ids()
- can_access_athlete()
- get_accessible_athletes()

### Security Features
- Row-level security (RLS) on all sensitive tables
- Automatic audit logging
- Team-based access control
- UUID primary keys
- Vector embeddings support (if pgvector available)

## 💰 Cost Information

**Current Setup (db-f1-micro in asia-south1):**
- Instance: ~$10/month
- Storage: ~$0.17/GB/month
- Network egress: First 1GB free, then $0.12/GB

**Shared core instance details:**
- 1 vCPU (shared)
- 0.6 GB RAM
- Perfect for development and testing

## 🔐 Security Notes

1. **Change the default password** before production use
2. **Restrict authorized networks** - currently open to your IP only
3. **Use Cloud SQL Proxy** for production connections (more secure than public IP)
4. **Enable SSL** for connections in production
5. **Backup policy**: Enable automated backups (currently off)

## 🚀 After Schema Setup

Once tables are created:

1. **Verify Setup**:
```sql
-- List all tables
\dt physio_app.*

-- Check sample data
SELECT * FROM physio_app.v_active_care_teams;

-- Count records
SELECT 'Users' as table_name, COUNT(*) FROM physio_app.users
UNION ALL SELECT 'Athletes', COUNT(*) FROM physio_app.athlete_profiles;
```

2. **Build Backend API** (Next major phase)
   - Node.js + Express/Fastify
   - PostgreSQL connection pool
   - JWT authentication
   - GraphQL or REST endpoints

3. **Connect Frontend to Backend**
   - Replace mock data with API calls
   - Implement authentication flow
   - Add video upload functionality

## 📝 Connection String for Backend

```javascript
// Node.js example
const { Pool } = require('pg');

const pool = new Pool({
  host: '34.93.206.105',
  port: 5432,
  database: 'moove_production',
  user: 'postgres',
  password: 'MooveSecure2026!',
  ssl: {
    rejectUnauthorized: false
  }
});

// Set current user for RLS
await pool.query("SELECT physio_app.set_current_user($1)", [userId]);

// Query with automatic RLS enforcement
const result = await pool.query(
  "SELECT * FROM physio_app.athlete_profiles WHERE status = 'active'"
);
```

## ❓ Troubleshooting

### Connection Refused
- Verify your IP is authorized: `gcloud sql instances describe moove-db`
- Check instance is running: Status should be RUNNABLE
- Verify password is correct

### Extension Not Available (pgvector)
- Comment out vector columns in schema files
- Or use JSONB as fallback for embeddings
- pgvector may not be available on db-f1-micro tier

### Permission Denied
- Ensure you're connecting as 'postgres' user
- Check schema search path: `SHOW search_path;`
- Set path: `SET search_path TO physio_app;`

---

**Ready to proceed?** Install PostgreSQL client and run the migrations! 🎯
