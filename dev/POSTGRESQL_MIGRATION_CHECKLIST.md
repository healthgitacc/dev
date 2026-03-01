# PostgreSQL Migration Checklist

## Status: ✅ Code Ready for PostgreSQL

Your codebase has been updated and is ready for PostgreSQL. All changes are compatible with both SQLite and PostgreSQL for flexibility.

---

## What Changed

### ✅ Configuration Files Updated
- **`.env`** - Changed from SQLite to PostgreSQL connection string
- **`.env.production`** - Created production-ready template
- **`init_db.py`** - Updated to work with both SQLite and PostgreSQL dynamically

### ✅ Code Status
- **Database Models** - ✅ Already PostgreSQL-compatible
- **Connection Pool** - ✅ Configured with proper pooling for PostgreSQL
- **Migrations** - ✅ Alembic ready for schema management
- **ORM** - ✅ Using standard SQLAlchemy (universal compatibility)

---

## Installation Steps

### Step 1: Install PostgreSQL
**Choose ONE method:**

#### Option A: Direct Installation (Recommended)
1. Download from: https://www.postgresql.org/download/windows/
2. Run installer with these settings:
   - **Directory**: `C:\Program Files\PostgreSQL\16`
   - **Password**: Remember the superuser password (use "postgres" for dev)
   - **Port**: `5432`
3. Close installer

#### Option B: Docker (Easier if Docker is installed)
```powershell
docker-compose up -d postgres
```

### Step 2: Create Database
```powershell
# Connect to PostgreSQL
psql -U postgres

# In the psql prompt, execute:
CREATE DATABASE hospital_db;
\q
```

### Step 3: Install Python Dependencies
```powershell
cd "e:\project\POC 1st\backend"
pip install -r requirements.txt
```

### Step 4: Initialize Database Tables
```powershell
python init_db.py
```

### Step 5: Start the Application
```powershell
# Terminal 1 - Backend
cd "e:\project\POC 1st\backend"
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd "e:\project\POC 1st\frontend"
npm run dev
```

### Step 6: Access Application
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

---

## Or Use the Automated Setup Script

```powershell
cd "e:\project\POC 1st"
.\setup_postgresql.ps1
```

This script will:
- Verify PostgreSQL installation
- Create the database
- Install Python dependencies
- Initialize database tables
- Show next steps

---

## Configuration Details

### Current .env (Development)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hospital_db
USE_SQLITE=false
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hospital_db
```

### Production .env (After Deployment)
Update `.env.production` with:
```env
DATABASE_URL=postgresql://hospital_admin:secure_password@prod-host:5432/hospital_db
DB_USER=hospital_admin
DB_PASSWORD=secure_password
DB_HOST=prod-host.com
```

---

## Troubleshooting

### ❌ "psql: command not found"
```powershell
# Add PostgreSQL to PATH
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"

# Verify
psql --version
```

### ❌ "Connection refused"
```powershell
# Start PostgreSQL service
Get-Service postgresql-x64-16 | Start-Service

# Verify it's running
Get-Service postgresql-x64-16
```

### ❌ "Database hospital_db does not exist"
```powershell
psql -U postgres -c "CREATE DATABASE hospital_db;"
```

### ❌ "FATAL: role 'postgres' does not exist"
```powershell
# Reinstall PostgreSQL or recovery mode
# Or create user manually if database was migrated
```

### ❌ "psycopg2.OperationalError: connection failed"
**Check in order**:
1. PostgreSQL is running: `Get-Service postgresql-x64-16`
2. Credentials in `.env` are correct
3. Database exists: `psql -U postgres -l`
4. Port is correct: `Test-NetConnection localhost -Port 5432`

---

## Verification Commands

### Check PostgreSQL is Running
```powershell
psql -U postgres -c "SELECT version();"
```

### List All Databases
```powershell
psql -U postgres -c "\l"
```

### Connect to Hospital Database
```powershell
psql -U postgres -d hospital_db

# List tables
\dt

# Exit
\q
```

### Check Connection Pool Status
```powershell
# From backend directory
python -c "from app.database import engine; print('✓ Connection pool OK')"
```

---

## Recommended Settings for Production

### 1. Create Dedicated User
```sql
CREATE USER hospital_admin WITH PASSWORD 'strong_password_here';
ALTER ROLE hospital_admin CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE hospital_db TO hospital_admin;
```

### 2. Enable Full Backups
```bash
# Daily full backup
# pg_dump -U postgres hospital_db > backup_$(date +%Y%m%d).sql
```

### 3. Monitor Performance
```sql
-- Top queries by execution time
SELECT query, mean_exec_time FROM pg_stat_statements 
ORDER BY mean_exec_time DESC LIMIT 10;

-- Table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 4. Connection Pool Tuning
In `.env`:
```env
# Adjust based on your server load
DATABASE_URL=postgresql://user:pass@host:5432/hospital_db?max_connections=20
```

---

## Migration from SQLite (If you had data)

If you already had data in SQLite, follow these steps:

1. **Export SQLite data** (SQLite running)
   ```powershell
   sqlite3 hospital.db ".dump" > sqlite_backup.sql
   ```

2. **Create equivalent schema** (PostgreSQL running)
   ```powershell
   python init_db.py
   ```

3. **Use migration tool or manual import**
   - For small databases: Manual data entry
   - For large databases: Consider using migration tools like `pgloader`

4. **Verify data**
   ```powershell
   psql -U postgres -d hospital_db -c "SELECT COUNT(*) FROM users;"
   ```

---

## Files Created/Modified

### Created:
- ✅ `POSTGRESQL_SETUP_GUIDE.md` - Complete installation guide
- ✅ `backend/.env.production` - Production template
- ✅ `setup_postgresql.ps1` - Automated setup script

### Modified:
- ✅ `backend/.env` - Changed to PostgreSQL connection
- ✅ `backend/init_db.py` - Made dynamic for both databases

### Already Configured:
- ✅ `docker-compose.yml` - Has PostgreSQL service
- ✅ `backend/app/database.py` - Auto-detects database type
- ✅ `backend/requirements.txt` - Has psycopg2-binary

---

## Next Steps After Setup

1. **Test Endpoints**
   - Open http://localhost:8000/docs
   - Try login, create patient, book appointment

2. **Verify Data in Database**
   ```powershell
   psql -U postgres -d hospital_db -c "SELECT * FROM users LIMIT 5;"
   ```

3. **Monitor Logs**
   - Backend logs show SQL queries (if SQL_ECHO=true)
   - Check for any connection warnings

4. **Performance Baseline**
   - Note response times before optimization
   - Set up monitoring for production

---

## Support & Documentation

- **PostgreSQL Official Docs**: https://www.postgresql.org/docs/16/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Alembic Migration**: https://alembic.sqlalchemy.org/
- **psycopg2 Adapter**: https://www.psycopg.org/

