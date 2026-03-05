# PostgreSQL Setup - Quick Reference

## ⚡ 5-Minute Setup

### Option 1: Automated Setup (Easiest)
```powershell
cd "e:\project\POC 1st"
.\setup_postgresql.ps1
```

### Option 2: Manual Setup
```powershell
# 1. Install PostgreSQL from https://www.postgresql.org/download/windows/
#    Remember the password you set!

# 2. Create database
psql -U postgres -c "CREATE DATABASE hospital_db;"

# 3. Install dependencies
cd "e:\project\POC 1st\backend"
pip install -r requirements.txt

# 4. Initialize database
python init_db.py

# 5. Run backend
python -m uvicorn app.main:app --reload

# 6. Run frontend (new terminal)
cd "e:\project\POC 1st\frontend"
npm run dev

# Access: http://localhost:3000
```

---

## 📋 Current Configuration

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hospital_db
USE_SQLITE=false
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hospital_db
```

---

## ✅ Verification

```powershell
# Check PostgreSQL running
Get-Service postgresql-x64-16

# Connect to database
psql -U postgres -d hospital_db

# List tables
psql -U postgres -d hospital_db -c "\dt"

# Count users
psql -U postgres -d hospital_db -c "SELECT COUNT(*) FROM users;"
```

---

## 🔗 Important Links

| What | Where |
|------|-------|
| Setup Guide | `POSTGRESQL_SETUP_GUIDE.md` |
| Checklist | `POSTGRESQL_MIGRATION_CHECKLIST.md` |
| Setup Script | `setup_postgresql.ps1` |
| Complete Details | `POSTGRESQL_MIGRATION_COMPLETE.md` |
| Production Template | `backend/.env.production` |

---

## ❌ Troubleshooting

| Problem | Solution |
|---------|----------|
| "psql not found" | Add to PATH: `C:\Program Files\PostgreSQL\16\bin` |
| "Connection refused" | Start service: `Get-Service postgresql-x64-16 \| Start-Service` |
| "Database not found" | Create: `psql -U postgres -c "CREATE DATABASE hospital_db;"` |
| "Import error: psycopg2" | Install: `pip install -r requirements.txt` |

---

## 🚀 Database is Ready!

Your code automatically:
- ✅ Detects PostgreSQL from `DATABASE_URL`
- ✅ Uses proper connection pooling
- ✅ Applies migrations automatically  
- ✅ Handles both SQLite and PostgreSQL

**Just install PostgreSQL and you're done!** 🎉

