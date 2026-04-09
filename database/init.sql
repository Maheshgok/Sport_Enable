-- ============================================
-- Database Initialization Script
-- Platform: Google Cloud SQL (PostgreSQL)
-- Project: Moove - Sports Injury Recovery Platform
-- ============================================

-- Enable required extensions
-- uuid-ossp: Provides UUID generation functions for primary keys
-- Create in public schema so it's accessible everywhere
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" SCHEMA public;

-- pgvector: Enables vector data type for biomechanical embeddings
-- Note: Ensure pgvector is available in your Cloud SQL instance
-- For Cloud SQL PostgreSQL, pgvector may need to be enabled via database flags
CREATE EXTENSION IF NOT EXISTS "vector" SCHEMA public;

-- Create application schema
CREATE SCHEMA IF NOT EXISTS physio_app;

-- Set default search path to include physio_app schema
-- This allows queries to reference tables without schema qualification
ALTER DATABASE moove_production SET search_path TO physio_app, public;

-- Set search path for current session
SET search_path TO physio_app, public;

-- Grant usage on schema to current user (adjust as needed for your application user)
GRANT USAGE ON SCHEMA physio_app TO CURRENT_USER;
GRANT CREATE ON SCHEMA physio_app TO CURRENT_USER;

-- Verify extensions are installed
SELECT extname, extversion FROM pg_extension WHERE extname IN ('uuid-ossp', 'vector');

-- Display created schema
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'physio_app';

-- ============================================
-- Notes for Cloud SQL Setup:
-- ============================================
-- 1. Ensure your Cloud SQL instance has the pgvector extension available
--    If not, you may need to:
--    - Use a PostgreSQL version that supports pgvector (14+)
--    - Enable via database flags: cloudsql.enable_pgvector=on
--    - Or use Cloud SQL for PostgreSQL with Enterprise Plus edition
--
-- 2. Run this script as a superuser or database owner:
--    psql -h <INSTANCE_IP> -U postgres -d <DATABASE_NAME> -f init.sql
--
-- 3. For production, create dedicated application user:
--    CREATE USER moove_app WITH PASSWORD 'secure_password';
--    GRANT USAGE ON SCHEMA physio_app TO moove_app;
--    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA physio_app TO moove_app;
--    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA physio_app TO moove_app;
-- ============================================
