# Quick Start - Database Setup

## 🚀 Fast Setup (5 minutes)

### 1. Create Cloud SQL Instance
```bash
gcloud config set project watch-mail-trial

gcloud sql instances create moove-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=asia-south1
```

### 2. Create Database
```bash
gcloud sql databases create moove_production --instance=moove-db
```

### 3. Set Root Password
```bash
gcloud sql users set-password postgres \
  --instance=moove-db \
  --password=YOUR_SECURE_PASSWORD
```

### 4. Connect via Cloud SQL Proxy
```bash
# Download and run proxy
cloud-sql-proxy watch-mail-trial:asia-south1:moove-db
```

### 5. Initialize Database
```bash
# In new terminal
psql "host=127.0.0.1 dbname=moove_production user=postgres" -f database/init.sql
```

## ✅ Verification Checklist

```sql
-- 1. Check extensions
\dx

-- Expected output:
-- uuid-ossp | <version>
-- vector    | <version> (if supported)

-- 2. Check schema
\dn

-- Expected output:
-- physio_app | <owner>

-- 3. Test UUID generation
SELECT uuid_generate_v4();

-- Expected: UUID string like '550e8400-e29b-41d4-a716-446655440000'
```

## 📊 Cost Estimate

- **db-f1-micro**: ~$10/month (development)
- **db-custom-2-7680**: ~$120/month (production)
- **Storage**: $0.17/GB/month
- **Egress**: $0.12/GB (after 1GB free tier)

## 🔐 Security Quick Setup

```sql
-- Create app user
CREATE USER moove_app WITH PASSWORD 'your_secure_password';
GRANT USAGE ON SCHEMA physio_app TO moove_app;
GRANT ALL ON ALL TABLES IN SCHEMA physio_app TO moove_app;
GRANT ALL ON ALL SEQUENCES IN SCHEMA physio_app TO moove_app;
```

## 🔗 Connection String Format

```
postgresql://moove_app:password@/moove_production?host=/cloudsql/watch-mail-trial:asia-south1:moove-db
```

## 🆘 Quick Troubleshooting

**Can't connect?**
```bash
# Check instance is running
gcloud sql instances list

# Check Cloud SQL Proxy is running
ps aux | grep cloud-sql-proxy
```

**pgvector not available?**
- Continue without it initially
- Use JSONB for embeddings
- Upgrade instance tier later if needed

**Permission errors?**
```sql
-- Re-grant permissions
GRANT ALL ON SCHEMA physio_app TO moove_app;
```

---

**Next**: Run table creation scripts in `database/schema/` directory
