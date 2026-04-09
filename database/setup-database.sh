#!/bin/bash
# Run this script in Google Cloud Shell to create all tables
# Usage: bash setup-database.sh

set -e  # Exit on any error

echo "============================================"
echo "Moove Database Setup - Cloud Shell"
echo "============================================"
echo ""

# Connection details
DB_INSTANCE="moove-db"
DB_NAME="moove_production"

echo "📡 Connecting to Cloud SQL instance: $DB_INSTANCE"
echo ""

# Download schema files from the repository (if running in Cloud Shell)
# Or manually upload files to Cloud Shell

echo "Running migrations..."
echo ""

# Connect and run init.sql
echo "1️⃣  Initializing extensions and schema..."
gcloud sql connect $DB_INSTANCE --user=postgres --database=$DB_NAME < init.sql

echo "2️⃣  Creating user tables..."
gcloud sql connect $DB_INSTANCE --user=postgres --database=$DB_NAME < schema/01_users_and_profiles.sql

echo "3️⃣  Creating relationship tables..."
gcloud sql connect $DB_INSTANCE --user=postgres --database=$DB_NAME < schema/02_relationships.sql

echo "4️⃣  Creating clinical data tables..."
gcloud sql connect $DB_INSTANCE --user=postgres --database=$DB_NAME < schema/03_clinical_data.sql

echo "5️⃣  Setting up access control..."
gcloud sql connect $DB_INSTANCE --user=postgres --database=$DB_NAME < schema/04_access_control.sql

echo "6️⃣  Loading sample data..."
gcloud sql connect $DB_INSTANCE --user=postgres --database=$DB_NAME < schema/05_sample_data.sql

echo ""
echo "============================================"
echo "✅ Database setup complete!"
echo "============================================"
echo ""
echo "Verify with:"
echo "  gcloud sql connect $DB_INSTANCE --user=postgres --database=$DB_NAME"
echo "  Then run: \\dt physio_app.*"
echo ""
