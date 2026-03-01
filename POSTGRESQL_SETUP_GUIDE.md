# PostgreSQL Setup Guide for Production

## Installation Guide for Windows

### Prerequisites
- Windows 10/11
- Administrator access
- ~300MB free disk space

---

## METHOD 1: Direct Installation (Recommended)

### Step 1: Download PostgreSQL
1. Go to: https://www.postgresql.org/download/windows/
2. Click **"Download the installer"**
3. Choose version **PostgreSQL 16** (or latest)
4. Download the **Windows x86-64** version

### Step 2: Install PostgreSQL
1. Run the installer (e.g., `postgresql-16-winx64-setup.exe`)
2. Follow the installation wizard:
   - **Installation Directory**: `C:\Program Files\PostgreSQL\16` ✓
   - **Select Components**: Keep all checked ✓
   - **Data Directory**: `C:\Program Files\PostgreSQL\16\data` ✓
   - **Superuser Password**: 
     - For local dev: `postgres` (or your choice)
     - **⚠️ IMPORTANT: Remember this password!**
   - **Port**: `5432` ✓
   - **Locale**: Default (use system locale) ✓
   - **Pre-installation Check**: Click Next
3. Click **Finish** to complete installation

### Step 3: Verify Installation
1. Open PowerShell as Administrator
2. Run:
   ```powershell
   psql --version
   ```
3. Expected output: `psql (PostgreSQL) 16.x`

### Step 4: Create Database and User
1. Connect to PostgreSQL as superuser:
   ```powershell
   psql -U postgres
   ```
2. When prompted for password, enter the password you set during installation

3. Execute the following SQL commands:
   ```sql
   -- Create hospital database
   CREATE DATABASE hospital_db;

   -- Create a dedicated user (optional but recommended for prod)
   CREATE USER hospital_admin WITH PASSWORD 'hospital_secure_password';

   -- Grant privileges
   ALTER ROLE hospital_admin CREATEDB;
   GRANT ALL PRIVILEGES ON DATABASE hospital_db TO hospital_admin;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hospital_admin;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hospital_admin;

   -- List databases to verify
   \l

   -- Exit
   \q
   ```

---

## METHOD 2: Using Docker (Alternative - Easier)

### Prerequisites
- Install Docker Desktop from: https://www.docker.com/products/docker-desktop/
- Restart computer after installation

### Step 1: Start PostgreSQL with Docker
```powershell
cd "e:\project\POC 1st"
docker-compose up -d postgres
```

### Step 2: Verify Container is Running
```powershell
docker-compose ps
```
Should show `postgres` container as **Up**

### Step 3: Create Database
```powershell
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE hospital_db;"
```

---

## Configuration Files Updated

### ✅ .env File
Your `.env` has been updated to use PostgreSQL:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hospital_db
USE_SQLITE=false
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hospital_db
```

**For production**, update credentials:
```env
DATABASE_URL=postgresql://hospital_admin:hospital_secure_password@prod-host:5432/hospital_db
DB_USER=hospital_admin
DB_PASSWORD=hospital_secure_password
DB_HOST=prod-host
DB_PORT=5432
DB_NAME=hospital_db
```

---

## Code Changes

### ✅ Database Configuration
Your code already supports both SQLite and PostgreSQL:

**Location**: `backend/app/database.py`
- ✅ Automatically detects PostgreSQL from `DATABASE_URL`
- ✅ Uses proper connection pooling (`pool_pre_ping`, `pool_recycle`)
- ✅ Includes SQLite fallback for development

---

## Running the Application with PostgreSQL

### Step 1: Install Python Dependencies
```powershell
cd "e:\project\POC 1st\backend"
pip install -r requirements.txt
```

### Step 2: Initialize Database (Run Migrations)
```powershell
# Apply all migrations
alembic upgrade head
```

### Step 3: Start the Backend Server
```powershell
cd "e:\project\POC 1st\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4: Start the Frontend (in new terminal)
```powershell
cd "e:\project\POC 1st\frontend"
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Troubleshooting

### ❌ "psql: command not found"
**Solution**: Add PostgreSQL to PATH
1. Press `Win + X` → Settings
2. System → About → Advanced system settings
3. Environment Variables
4. Add to PATH: `C:\Program Files\PostgreSQL\16\bin`
5. Restart PowerShell

### ❌ "FATAL: role 'postgres' does not exist"
**Solution**: Create the superuser role
```powershell
# Find PostgreSQL data directory
cd "C:\Program Files\PostgreSQL\16\data"

# Create superuser (Windows will prompt for password)
"C:\Program Files\PostgreSQL\16\bin\initdb" -D "C:\Program Files\PostgreSQL\16\data" -U postgres
```

### ❌ "Connection refused" on port 5432
**Solution**: PostgreSQL service not running
```powershell
# Start PostgreSQL service
Get-Service postgresql-x64-16 | Start-Service

# Verify it's running
Get-Service postgresql-x64-16
```

### ❌ "ERROR: database 'hospital_db' does not exist"
**Solution**: Create the database
```powershell
psql -U postgres -c "CREATE DATABASE hospital_db;"
```

### ❌ "psycopg2.OperationalError: connection failed"
**Verify**:
1. PostgreSQL is running: `psql -U postgres -c "SELECT 1;"`
2. Database exists: `psql -U postgres -l`
3. Credentials in `.env` match your setup
4. Port 5432 is accessible: `Test-NetConnection localhost -Port 5432`

---

## Database Features in PostgreSQL

Your code automatically uses these PostgreSQL features:

### ✅ Connection Pooling
- Maintains 5 connections by default
- Auto-recycles connections every 1 hour
- Pre-pings connections to verify availability

### ✅ Advanced Features
- UUID types for better performance
- JSONB support for flexible data
- Full-text search capabilities
- Advanced indexing options
- Transaction support across tables

### ✅ Data Integrity
- Foreign key constraints enforced
- Check constraints for data validation
- Unique constraints on email fields
- Default values for timestamps

---

## Migration to PostgreSQL from SQLite

Your data will be migrated using Alembic:

```powershell
# Check current migration status
alembic current

# Apply pending migrations
alembic upgrade head

# To rollback (if needed)
alembic downgrade -1
```

---

## Production Deployment Checklist

- [ ] PostgreSQL installed on production server
- [ ] Database credentials secured in environment variables
- [ ] Connection pooling configured for your scale
- [ ] Backups configured daily
- [ ] Monitoring/logging enabled
- [ ] SSL certificates for DB connection
- [ ] Firewall rules restrict DB access
- [ ] Database user has minimum required permissions
- [ ] Connection string uses production credentials

---

## Performance Tips for PostgreSQL

1. **Enable achievements after setup**:
   ```sql
   ANALYZE;
   ANALYZE hospital_db;
   ```

2. **Monitor queries**:
   ```sql
   SELECT query, calls FROM pg_stat_statements ORDER BY calls DESC LIMIT 10;
   ```

3. **Check index usage**:
   ```sql
   SELECT schemaname, tablename, indexname FROM pg_indexes;
   ```

---

## Next Steps
1. Install PostgreSQL using one of the methods above
2. Create the hospital_db database
3. Run migrations: `alembic upgrade head`
4. Start the application
5. Verify in API docs: http://localhost:8000/docs

**Questions?** Check the troubleshooting section or refer to PostgreSQL documentation: https://www.postgresql.org/docs/16/

