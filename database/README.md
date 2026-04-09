# Database Setup - Cloud SQL (PostgreSQL)

## Overview
This directory contains SQL scripts for initializing the Moove application database on Google Cloud Platform using Cloud SQL for PostgreSQL.

## Prerequisites

### 1. Cloud SQL Instance Requirements
- **PostgreSQL Version**: 14 or higher (required for pgvector)
- **Instance Tier**: Recommended Enterprise Plus for pgvector support
- **Database Flags**: 
  - `cloudsql.enable_pgvector=on` (if available)
  - `max_connections=100` (adjust based on workload)

### 2. Extensions Required
- **uuid-ossp**: UUID generation (included in standard PostgreSQL)
- **pgvector**: Vector similarity search for biomechanical embeddings

### 3. Client Tools
```bash
# Install PostgreSQL client
# For Windows (via Chocolatey):
choco install postgresql

# Or use Cloud SQL Proxy
gcloud components install cloud-sql-proxy
```

## Setup Instructions

### Step 1: Create Cloud SQL Instance
```bash
# Set project
gcloud config set project watch-mail-trial

# Create PostgreSQL instance (adjust region/tier as needed)
gcloud sql instances create moove-db \
  --database-version=POSTGRES_14 \
  --tier=db-custom-2-7680 \
  --region=asia-south1 \
  --database-flags=cloudsql.enable_pgvector=on

# Create database
gcloud sql databases create moove_production \
  --instance=moove-db
```

### Step 2: Connect to Database
```bash
# Option A: Using Cloud SQL Proxy (recommended for local development)
cloud-sql-proxy watch-mail-trial:asia-south1:moove-db --port=5432

# Then connect via psql
psql "host=127.0.0.1 port=5432 dbname=moove_production user=postgres"

# Option B: Direct connection (requires allowlisted IP)
psql "host=<INSTANCE_IP> dbname=moove_production user=postgres sslmode=require"
```

### Step 3: Run Initialization Script
```bash
# From the database directory
psql "host=127.0.0.1 port=5432 dbname=moove_production user=postgres" -f init.sql
```

### Step 4: Verify Setup
```sql
-- Check extensions
SELECT extname, extversion FROM pg_extension 
WHERE extname IN ('uuid-ossp', 'vector');

-- Check schema
\dn physio_app

-- Test UUID generation
SELECT uuid_generate_v4();

-- Test vector extension (if supported)
SELECT '[1,2,3]'::vector;
```

## pgvector Considerations

### Vector Embedding Use Cases
In the Moove platform, pgvector will be used for:
- **Movement analysis embeddings**: Store video frame feature vectors for similarity search
- **Exercise recommendations**: Match biomechanical patterns to exercise library
- **Progress tracking**: Compare movement quality over time using vector similarity

### Vector Column Examples
```sql
-- Example table with vector column
CREATE TABLE physio_app.movement_embeddings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  athlete_id UUID NOT NULL,
  assessment_id UUID NOT NULL,
  frame_timestamp INTEGER NOT NULL,
  embedding vector(512),  -- 512-dimensional embedding
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for fast similarity search
CREATE INDEX ON physio_app.movement_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Similarity Search Query
```sql
-- Find similar movements (cosine similarity)
SELECT athlete_id, assessment_id, 
       1 - (embedding <=> '[0.1, 0.2, ...]'::vector) as similarity
FROM physio_app.movement_embeddings
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

## Alternative: If pgvector is Unavailable

If your Cloud SQL instance doesn't support pgvector:

### Option 1: Use JSON for embeddings
```sql
-- Store as JSONB instead
ALTER TABLE movement_embeddings 
  ALTER COLUMN embedding TYPE JSONB USING embedding::text::jsonb;
```

### Option 2: External vector database
- Use Pinecone or Weaviate for vector operations
- Store reference IDs in Cloud SQL
- Perform similarity search in external service

### Option 3: Upgrade to supporting tier
- Use Cloud SQL Enterprise Plus edition
- Or migrate to Cloud Spanner with vector support

## Security Recommendations

### 1. Create Application User
```sql
-- Create dedicated user with limited privileges
CREATE USER moove_app WITH PASSWORD 'SECURE_PASSWORD_HERE';
GRANT USAGE ON SCHEMA physio_app TO moove_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA physio_app TO moove_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA physio_app TO moove_app;

-- Grant default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA physio_app 
GRANT ALL ON TABLES TO moove_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA physio_app 
GRANT ALL ON SEQUENCES TO moove_app;
```

### 2. Connection from Firebase/Cloud Run
```javascript
// Use Cloud SQL Proxy or private IP connection
const { Pool } = require('pg');

const pool = new Pool({
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  // For Cloud Run with Cloud SQL connector:
  host: `/cloudsql/${process.env.INSTANCE_CONNECTION_NAME}`,
  // For external connection:
  // host: process.env.DB_HOST,
  // port: 5432,
  // ssl: { rejectUnauthorized: false }
});
```

### 3. Environment Variables
```bash
# Store in .env.local (never commit)
DB_USER=moove_app
DB_PASSWORD=your_secure_password
DB_NAME=moove_production
DB_HOST=10.x.x.x  # Private IP
INSTANCE_CONNECTION_NAME=watch-mail-trial:asia-south1:moove-db
```

## Database Schema Files

The schema is organized into multiple files for maintainability:

### Migration Files (in order)
1. **init.sql** - Extensions (uuid-ossp, pgvector) and schema creation
2. **schema/01_users_and_profiles.sql** - User accounts and role-specific profiles
3. **schema/02_relationships.sql** - Athlete team assignments (1:1:1:1 relationships)
4. **schema/03_clinical_data.sql** - Assessments, exercises, progress tracking
5. **schema/04_access_control.sql** - Row-level security and access functions
6. **schema/05_sample_data.sql** - Seed data for testing (optional)

### Quick Setup
```bash
# Run all migrations at once
psql "host=127.0.0.1 dbname=moove_production user=postgres" -f database/run_all.sql

# Or run individually
psql "host=127.0.0.1 dbname=moove_production user=postgres" -f database/init.sql
psql "host=127.0.0.1 dbname=moove_production user=postgres" -f database/schema/01_users_and_profiles.sql
# ... etc
```

## Schema Overview

### Core Tables
- **users** (1) → **athlete_profiles** (1)
- **users** (1) → **physiotherapist_profiles** (N)
- **users** (1) → **coach_profiles** (N)
- **users** (1) → **caretaker_profiles** (N)
- **athlete_teams** - Junction table enforcing 1:1:1:1 care team relationships

### Clinical Tables
- **assessments** - Physical and video assessments
- **exercise_library** - Master exercise database
- **exercise_assignments** - Prescribed exercises
- **exercise_sessions** - Completed workout logs
- **daily_tasks** - Daily care tasks
- **progress_milestones** - Recovery goals and achievements
- **clinical_notes** - Care team observations

### Security Features
- Row-level security (RLS) on all sensitive tables
- Access control functions: `can_access_athlete()`, `get_accessible_athletes()`
- Audit logging for compliance
- Session-based user context: `set_current_user()`

## Next Steps

1. ✅ Initialize database with extensions and schema (init.sql)
2. ✅ Create user and role tables (schema/01_users_and_profiles.sql)
3. ✅ Create relationship tables (schema/02_relationships.sql)
4. ✅ Create clinical data tables (schema/03_clinical_data.sql)
5. ✅ Set up access control (schema/04_access_control.sql)
6. ✅ Load sample data (schema/05_sample_data.sql)
7. ⏳ Build backend API
8. ⏳ Connect frontend to database

## Cost Optimization

- **Development**: Use db-f1-micro tier (~$10/month)
- **Production**: Scale up to db-custom based on load
- **Backups**: Enable automated backups (7-day retention recommended)
- **High Availability**: Enable for production workloads

## Troubleshooting

### pgvector not available
```bash
# Check available extensions
gcloud sql instances describe moove-db \
  --format="value(settings.databaseFlags)"

# If pgvector missing, proceed without vector support initially
# Implement using JSONB embeddings as fallback
```

### Connection refused
- Ensure Cloud SQL Proxy is running
- Check firewall rules allow your IP
- Verify SSL mode configuration

### Permission denied
- Ensure user has proper grants on schema
- Check default privileges are set correctly
