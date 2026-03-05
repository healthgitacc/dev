# Phase 6 Setup & Testing Guide

## Overview
Phase 6 implementation includes:
- ✅ Notification Service (SMS via Twilio + mock mode)
- ✅ Background Scheduler (APScheduler for reminder jobs)
- ✅ Docker containerization (multi-stage build)
- ✅ Alembic migrations framework
- ✅ Initial database schema migration

## Prerequisites
- Docker Desktop installed and running
- Docker Compose installed (included with Docker Desktop)
- Git (for cloning if needed)
- Python 3.10+ (for local testing without Docker)

## Quick Start - Using Docker Compose

### Step 1: Prepare Environment Variables
```bash
cd backend
cp .env.example .env
```

Edit `.env` and set:
```
DB_USER=hospital_user
DB_PASSWORD=hospital_password_123
DB_HOST=postgres
DB_PORT=5432
DB_NAME=hospital_db
REMINDER_HOUR=8
REMINDER_MINUTE=0
REMINDER_HOURS_BEFORE=24
SECRET_KEY=your-secret-key-must-be-at-least-32-characters-long!!!
TWILIO_ACCOUNT_SID=mock_account_sid
TWILIO_AUTH_TOKEN=mock_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

### Step 2: Build and Start Services
```bash
cd ..  # Back to project root
docker-compose up --build
```

Expected logs:
```
postgres   | database system is ready to accept connections
backend    | INFO:     Started server process
backend    | INFO:     Scheduler initialized and started successfully
backend    | INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Verify Services
```bash
# In another terminal
curl http://localhost:8000/health
# Expected: {"status": "ok"}

curl http://localhost:8000/
# Expected: {"message": "Welcome to Hospital Appointment & Medical Record Management API"}
```

### Step 4: Test API Authentication
```bash
# Register a new admin user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Admin User",
    "email": "admin@hospital.com",
    "password": "SecurePass123!",
    "phone": "1234567890",
    "role": "admin"
  }'

# Expected response includes JWT token
# Copy token and test authenticated endpoint
curl -X GET http://localhost:8000/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Database Management

### View Database (PgAdmin)
- URL: http://localhost:5050
- Email: admin@pgadmin.org
- Password: admin
- Add server: hostname=postgres, username=hospital_user, password=hospital_password_123

### Run Migrations Manually
```bash
# Connect to running container
docker exec -it hospital-backend bash

# View migration history
alembic current
alembic history

# Upgrade to latest
alembic upgrade head

# Downgrade (if needed)
alembic downgrade -1
```

### Connect to PostgreSQL Directly
```bash
docker exec -it hospital-postgres psql -U hospital_user -d hospital_db

# List tables
\dt

# View users table
SELECT * FROM users;
```

## Testing Appointment Reminder Scheduler

### Create Test Data
```bash
# 1. Register admin, doctor, and patient
# 2. Create appointment within next 24 hours
POST /appointments {
  "doctor_id": 1,
  "patient_id": 1,
  "appointment_date": "2025-02-25T10:00:00",
  "duration_minutes": 30,
  "notes": "Regular checkup"
}

# 3. Check container logs for scheduler jobs
docker-compose logs backend | grep -i "scheduler\|reminder"
```

### Verify Scheduler Running
```bash
# In container logs, look for:
# "INFO:     Scheduler initialized and started successfully"
# "INFO:     Daily reminder job scheduled for 08:00 UTC"
# "INFO:     Hourly cleanup job scheduled"
```

### Manual Reminder Trigger (for testing without waiting)
```bash
# Connect to container
docker exec -it hospital-backend bash

# Run Python to trigger reminders
python -c "
from app.tasks.reminder_scheduler import send_appointment_reminders
from app.database import SessionLocal
with SessionLocal() as db:
    send_appointment_reminders(db)
"
```

## Debug Mode

### Enable Verbose Logging
Edit `docker-compose.yml` backend section, add:
```yaml
environment:
  - LOG_LEVEL=DEBUG
  - DEBUG=true
```

### View Real-time Logs
```bash
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Container Shell Access
```bash
# Backend container
docker exec -it hospital-backend bash

# PostgreSQL container
docker exec -it hospital-postgres psql -U hospital_user -d hospital_db
```

## Common Issues & Solutions

### Issue: "Connection refused" connecting to postgres
**Solution:**
```bash
# Check if postgres service is healthy
docker-compose ps

# View postgres logs for errors
docker-compose logs postgres

# Restart services
docker-compose down -v
docker-compose up --build
```

### Issue: "Alembic migration failed"
**Solution:**
```bash
# Check migration status
docker exec -it hospital-backend alembic current

# Check migration history
docker exec -it hospital-backend alembic history

# Reset (WARNING: deletes all data)
docker exec -it hospital-postgres psql -U hospital_user -d hospital_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker-compose down -v
docker-compose up --build
```

### Issue: "Scheduler not starting"
**Solution:**
```bash
# Check app logs for errors
docker-compose logs backend | tail -50

# Verify APScheduler is installed
docker exec -it hospital-backend pip show apscheduler

# Restart containers
docker-compose restart backend
```

### Issue: "SMS notifications not sending"
**Solution:**
- Development mode: Notifications logged to console and database
- Check logs: `docker-compose logs backend | grep -i "sms\|reminder"`
- To enable Twilio: Set TWILIO credentials in `.env` and `DEBUG=false`
- Mock SMS output format: `[MOCK SMS] To: {phone}, Body: {message}`

## Local Development (Without Docker)

### Setup Virtual Environment
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

### Create .env File
```bash
cp .env.example .env
# Edit with local database credentials
```

### Initialize Database
```bash
# Create PostgreSQL database locally
# Then run migrations
alembic upgrade head
```

### Start Development Server
```bash
uvicorn app.main:app --reload --port 8000
```

## API Testing with Sample Data

### 1. Create Admin
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr Admin",
    "email": "admin@hospital.com",
    "password": "AdminPass123!",
    "phone": "9999999999",
    "role": "admin"
  }'
```

### 2. Create Doctor
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr John Smith",
    "email": "john.smith@hospital.com",
    "password": "DoctorPass123!",
    "phone": "8888888888",
    "role": "doctor",
    "specialization": "Cardiology",
    "experience_years": 10,
    "license_number": "LIC123456"
  }'
```

### 3. Create Patient
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@email.com",
    "password": "PatientPass123!",
    "phone": "7777777777",
    "role": "patient",
    "age": 35,
    "gender": "male",
    "blood_group": "O+",
    "medical_history": "Hypertension"
  }'
```

### 4. Create Appointment
```bash
curl -X POST http://localhost:8000/appointments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer PATIENT_TOKEN" \
  -d '{
    "doctor_id": 1,
    "patient_id": 1,
    "appointment_date": "2025-02-26T10:00:00",
    "duration_minutes": 30,
    "notes": "Annual checkup"
  }'
```

### 5. Get Upcoming Reminders
```bash
curl -X GET "http://localhost:8000/appointments/upcoming/reminders?hours_before=24" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## Performance Testing

### Load Testing (using Apache Bench)
```bash
# First, get an auth token
TOKEN="your_token_here"

# Test endpoint
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" http://localhost:8000/doctors
```

### Database Query Performance
```bash
# Connect to postgres
docker exec -it hospital-postgres psql -U hospital_user -d hospital_db

# Check slow queries log
EXPLAIN ANALYZE SELECT * FROM appointments WHERE doctor_id = 1;

# Check index usage
SELECT * FROM pg_stat_user_indexes;
```

## What's Ready for Phase 7 (Frontend)

After Phase 6 is complete:
- ✅ Backend API fully functional with 37+ endpoints
- ✅ Database with all relationships and indexes
- ✅ Authentication system (JWT tokens)
- ✅ Background scheduler running
- ✅ Docker deployment ready

Next Phase: Frontend Development
- Next.js 14 with App Router
- Tailwind CSS styling
- Role-based page routing
- Login & Dashboard components
- API integration with JWT authentication
- Form components for appointments/medical records

## Troubleshooting Commands Reference

```bash
# Check all services
docker-compose ps

# View logs for specific service
docker-compose logs backend
docker-compose logs postgres

# Follow logs in real-time
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Run commands in container
docker exec -it hospital-backend bash
docker exec -it hospital-postgres psql -U hospital_user -d hospital_db

# Check resource usage
docker stats

# View network connections
docker network ls
docker network inspect hospital_network

# Verify migrations
docker exec -it hospital-backend alembic current
docker exec -it hospital-backend alembic history
```

## Environment Variables Reference

```
# Database
DB_USER=hospital_user
DB_PASSWORD=hospital_password_123
DB_HOST=postgres
DB_PORT=5432
DB_NAME=hospital_db
SQL_ECHO=false

# Application
DEBUG=true
SECRET_KEY=your-secret-key-min-32-chars-required
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Reminders
REMINDER_HOUR=8
REMINDER_MINUTE=0
REMINDER_HOURS_BEFORE=24

# Twilio (Optional - for production SMS)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

## Next Steps

1. ✅ **Verify Docker Compose works**: `docker-compose up --build`
2. ✅ **Test basic API endpoints**: Register and login users
3. ✅ **Check scheduler initialization**: Look for scheduler logs
4. ✅ **Test appointment reminders**: Create appointment and verify reminder job
5. ⏳ **Phase 7 - Frontend**: Set up Next.js 14 with role-based routing

**Ready to proceed to Phase 7 (Frontend)?** Type `next` to continue with Next.js setup.
