-- ============================================
-- Master Migration Script
-- Description: Runs all schema migrations in correct order
-- Usage: psql -h localhost -U postgres -d moove_production -f run_all.sql
-- ============================================

\echo '============================================'
\echo 'Moove Database Setup - Starting Migration'
\echo '============================================'
\echo ''

-- Set client encoding
SET client_encoding = 'UTF8';

\echo '>>> Step 1: Database Initialization (extensions and schema)'
\i init.sql
\echo ''

\echo '>>> Step 2: Users and Role Profiles'
\i schema/01_users_and_profiles.sql
\echo ''

\echo '>>> Step 3: Relationship Tables'
\i schema/02_relationships.sql
\echo ''

\echo '>>> Step 4: Clinical Data Tables'
\i schema/03_clinical_data.sql
\echo ''

\echo '>>> Step 5: Access Control & Security'
\i schema/04_access_control.sql
\echo ''

\echo '>>> Step 6: Sample Data (Optional - comment out for production)'
\i schema/05_sample_data.sql
\echo ''

\echo '============================================'
\echo 'Migration Complete!'
\echo '============================================'
\echo ''
\echo 'Next steps:'
\echo '1. Verify tables: \dt physio_app.*'
\echo '2. Check sample data: SELECT * FROM physio_app.v_active_care_teams;'
\echo '3. Test access control: SELECT physio_app.set_current_user(''user-uuid'');'
\echo ''
