# 🏥 Hospital Appointment & Medical Record Management System

A production-ready full-stack hospital management system built with FastAPI, PostgreSQL, and Next.js.

**Status:** Backend Complete (Phase 6 ✅) | Ready for Frontend (Phase 7 🚀)

---

## 📋 Quick Start

### Using Docker (Recommended)
```bash
# Start all services
docker-compose up --build

# In another terminal, run tests
python test_endpoints.py

# API available at: http://localhost:8000
# PgAdmin available at: http://localhost:5050
```

### Local Development
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | Complete project guide and navigation |
| [PHASE_6_COMPLETE.md](PHASE_6_COMPLETE.md) | Phase 6 implementation details |
| [PHASE_6_SETUP.md](PHASE_6_SETUP.md) | Setup, troubleshooting, and examples |
| [PHASE_6_VERIFICATION.md](PHASE_6_VERIFICATION.md) | Verification checklist |

### Quick Links
- **API Testing:** Run `python test_endpoints.py`
- **API Documentation:** Visit http://localhost:8000/docs (Swagger UI)
- **Database Admin:** Visit http://localhost:5050 (PgAdmin)
- **Health Check:** `curl http://localhost:8000/health`

---

## 🎯 System Features

### Authentication & Authorization
- ✅ JWT token-based authentication
- ✅ Role-based access control (admin/doctor/patient)
- ✅ Password hashing with bcrypt

### Appointment Management
- ✅ Create, update, reschedule appointments
- ✅ Automatic conflict detection
- ✅ Status tracking and transitions
- ✅ SMS reminders (Twilio integration)

### Medical Records
- ✅ Create and manage patient records
- ✅ Track diagnoses and prescriptions
- ✅ Schedule follow-up appointments
- ✅ Doctor-patient associations

### Background Jobs
- ✅ Appointment reminder scheduler (APScheduler)
- ✅ Configurable reminder timing
- ✅ SMS notifications (dev mock mode)
- ✅ Automatic cleanup jobs

### REST API
- ✅ 37+ endpoints across 6 domains
- ✅ Pagination and filtering
- ✅ Comprehensive error handling
- ✅ Request validation with Pydantic

---

## 🏗️ Architecture

### Backend Stack
- **Framework:** FastAPI 0.104.1
- **Database:** PostgreSQL 15 (SQLAlchemy ORM)
- **Authentication:** JWT (python-jose)
- **Password:** Bcrypt (passlib)
- **Scheduler:** APScheduler 3.10.4
- **Notifications:** Twilio SMS API
- **Deployment:** Docker + Docker Compose

### Database Schema
```
Users (admin/doctor/patient)
├── Doctors (specialization, license)
└── Patients (medical history, blood type)

Appointments (status tracking)
├── Doctor FK
├── Patient FK
└── Medical Records (diagnoses, prescriptions)
```

### API Endpoints (37+)
| Domain | Endpoints | Status |
|--------|-----------|--------|
| Auth | 4 | ✅ register, login, change-password, me |
| Users | 7 | ✅ list, get, search, stats, activate, deactivate |
| Doctors | 6 | ✅ list, get, search, specialization, profile |
| Patients | 7 | ✅ list, get, search, filter, profile |
| Appointments | 7 | ✅ create, get, update, reschedule, cancel, reminders |
| Medical Records | 7 | ✅ create, get, update, search, follow-ups |

---

## 🔧 Environment Setup

### Required Environment Variables
```bash
# Database
DB_USER=hospital_user
DB_PASSWORD=your_password
DB_HOST=postgres  # or localhost
DB_PORT=5432
DB_NAME=hospital_db

# Application
SECRET_KEY=min-32-characters-required
DEBUG=true  # false in production

# Scheduler
REMINDER_HOUR=8
REMINDER_MINUTE=0
REMINDER_HOURS_BEFORE=24

# Notifications
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
```

### Setup
```bash
cd backend
cp .env.example .env
# Edit .env with your values
```

---

## 🧪 Testing

### Comprehensive Test Suite
```bash
# Run all tests (requires running backend)
python test_endpoints.py

# Tests:
# ✓ Health check endpoint
# ✓ User registration with roles
# ✓ JWT authentication
# ✓ All 37+ API endpoints
# ✓ Appointment conflict detection
# ✓ Authorization and error handling
```

### Manual API Testing
```bash
# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "role": "patient"
  }'

# Login and get token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }' | jq -r '.access_token')

# Use token for authenticated requests
curl -X GET http://localhost:8000/appointments \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 Database Access

### Via Docker
```bash
# Connect to PostgreSQL
docker exec -it hospital-postgres psql -U hospital_user -d hospital_db

# List all tables
\dt

# View appointments
SELECT * FROM appointments;

# Exit
\q
```

### Via PgAdmin
- URL: http://localhost:5050
- Email: admin@pgadmin.org
- Password: admin
- Add server: hostname=postgres, user=hospital_user

---

## 🚀 Deployment

### Docker Compose (Full Stack)
```bash
# Start all services
docker-compose up --build

# Services:
# - PostgreSQL (port 5432)
# - FastAPI Backend (port 8000)
# - PgAdmin (port 5050)

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend
```

### Production Checklist
- ✅ Set `DEBUG=false` in .env
- ✅ Generate strong `SECRET_KEY` (32+ characters)
- ✅ Configure real Twilio credentials
- ✅ Set proper `ALLOWED_ORIGINS` for frontend
- ✅ Use production database host/credentials
- ✅ Enable HTTPS in production
- ✅ Set up monitoring and logging

---

## 📝 API Documentation

### Interactive Swagger UI
Visit http://localhost:8000/docs when backend is running

### Example Workflows

#### 1. User Registration & Login
```bash
# Register
POST /auth/register
{
  "name": "Dr. Smith",
  "email": "smith@hospital.com",
  "password": "DoctorPass123!",
  "role": "doctor",
  "specialization": "Cardiology",
  "experience_years": 10
}

# Login
POST /auth/login
{
  "email": "smith@hospital.com",
  "password": "DoctorPass123!"
}

# Response includes JWT token
```

#### 2. Create Appointment
```bash
# Patient creates appointment with doctor
POST /appointments
{
  "doctor_id": 1,
  "patient_id": 1,
  "appointment_date": "2025-02-26T10:00:00",
  "duration_minutes": 30,
  "notes": "Checkup"
}

# System checks:
# ✓ Doctor availability (no overlapping appointments)
# ✓ Patient availability (no overlapping appointments)
# ✗ Raises error if conflict detected
```

#### 3. Manage Medical Records
```bash
# Doctor creates medical record
POST /medical-records
{
  "patient_id": 1,
  "disease_name": "Hypertension",
  "diagnosis": "High blood pressure",
  "prescription_text": "Metoprolol",
  "dosage": "50mg daily",
  "follow_up_date": "2025-03-26T00:00:00"
}
```

---

## 🔒 Security Features

### Authentication
- JWT tokens with 30-minute expiration
- HTTPBearer scheme for API calls
- Password strength validation (8+ chars, uppercase, lowercase, digit, special char)

### Authorization
- Admin: Full access to all resources
- Doctor: Access to own profile and patient appointments
- Patient: Access to own profile, appointments, and medical records

### Data Protection
- CORS enabled for frontend origin
- SQL injection prevention (parameterized queries)
- No sensitive data in logs
- Cascading deletes to prevent orphaned data

---

## 📊 Performance Optimizations

### Database
- Strategic indexes on frequently queried fields
- Composite index for doctor appointment queries
- Connection pooling (SQLAlchemy)
- Pagination on all list endpoints

### API
- Async/await throughout FastAPI
- Efficient SQL queries in service layer
- HTTP caching headers
- Gzip compression support

### Scheduler
- Background thread (non-blocking)
- Efficient database queries
- Marker to prevent duplicate reminders
- Cleanup jobs to manage data growth

---

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs

# Ensure ports are available (8000, 5432, 5050)
# Or change ports in docker-compose.yml
```

### Database Connection Error
```bash
# Restart services
docker-compose down
docker-compose up --build

# Check PostgreSQL is healthy
docker-compose ps
```

### Migrations Failed
```bash
# Check migration status
docker exec hospital-backend alembic current

# View migration history
docker exec hospital-backend alembic history

# Rollback and retry
docker exec hospital-backend alembic downgrade -1
docker-compose restart backend
```

### Scheduler Not Running
```bash
# Check logs for scheduler initialization
docker-compose logs backend | grep -i scheduler

# Verify in container
docker exec hospital-backend ps aux | grep python
```

See [PHASE_6_SETUP.md](PHASE_6_SETUP.md) for more troubleshooting.

---

## 📈 Project Phases

### ✅ Phase 1: Project Setup
- Repository structure with clean architecture
- Database configuration
- Requirements and dependencies

### ✅ Phase 2: Database Models
- 5 SQLAlchemy ORM models
- Relationships and foreign keys
- Enum types for roles and statuses

### ✅ Phase 3: Security Layer
- JWT authentication
- Password hashing with bcrypt
- Role-based authorization
- Custom exceptions and logging

### ✅ Phase 4: Services Layer
- 8 business logic services
- Appointment conflict detection
- Medical record management
- No business logic in routes

### ✅ Phase 5: REST API
- 37+ endpoints across 6 domains
- Role-based access control
- Pagination and filtering
- Comprehensive error handling

### ✅ Phase 6: Production Deployment
- Notification service (SMS + mock)
- Background scheduler (APScheduler)
- Docker containerization
- Database migrations (Alembic)
- Testing suite and documentation

### 🚀 Phase 7: Frontend Development (Next)
- Next.js 14 with App Router
- TypeScript configuration
- Tailwind CSS styling
- Authentication pages
- Role-based dashboards
- Appointment booking UI
- Medical records viewer
- Responsive design

---

## 🤝 Project Structure Philosophy

### Clean Architecture Principles
1. **Separation of Concerns:** Models, schemas, services, routes kept separate
2. **Business Logic in Services:** All logic in `app/services/`, never in routes
3. **Dependency Injection:** FastAPI `Depends()` for database and auth
4. **Type Safety:** Type hints throughout, Pydantic validation
5. **Error Handling:** Custom exception hierarchy with HTTP status mapping

### Design Patterns Used
- Service Layer Pattern: Business logic isolation
- Repository Pattern: Generic BaseService[T] CRUD
- Dependency Injection: FastAPI dependencies
- Singleton: Scheduler instance management
- Factory: Service initialization
- Enum: Role and status types

---

## 📞 Support Resources

### Documentation
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Complete system guide
- [PHASE_6_COMPLETE.md](PHASE_6_COMPLETE.md) - Phase 6 details
- [PHASE_6_SETUP.md](PHASE_6_SETUP.md) - Setup and troubleshooting

### Testing
- `python test_endpoints.py` - Run comprehensive API tests
- http://localhost:8000/docs - Interactive API documentation

### Database
- http://localhost:5050 - PgAdmin web interface
- `docker exec hospital-postgres psql` - Direct database access

---

## 📄 License

This project is provided as-is for educational and development purposes.

---

## ✨ What's Next?

**Phase 6 Complete!** ✅

The backend is production-ready with:
- ✅ 37+ API endpoints
- ✅ Appointment scheduling with conflict detection
- ✅ Background reminders and notifications
- ✅ Full Docker deployment
- ✅ Database migrations
- ✅ Comprehensive testing

**Ready for Phase 7?** Type `next` to proceed with **Frontend Development** using Next.js 14

---

**Built with ❤️ as a production-ready hospital management system**

🚀 Full Stack Implementation | 📦 Docker Ready | 🔒 Secure Authentication | 📊 Complete API | ✨ Production Quality
