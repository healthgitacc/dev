# Hospital Flow Implementation - Setup & Testing Guide

## Quick Start: Creating Test Accounts

### 1. ADMIN ACCOUNT (Already Created)
The system should have a default admin account. If not, create one by registering:

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "System Admin",
    "email": "admin@hospital.com",
    "password": "AdminPass123!",
    "phone": "+1234567890",
    "role": "admin"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "admin@hospital.com",
  "role": "admin"
}
```

---

### 2. HOSPITAL STAFF ACCOUNT (Admin Creates)

The Admin creates a Hospital Staff account using their token:

```bash
curl -X POST "http://localhost:8000/api/staff/register" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {ADMIN_TOKEN}" \
  -d '{
    "name": "John Smith",
    "email": "staff@hospital.com",
    "password": "StaffPass123!",
    "phone": "+1987654321",
    "department": "Front Desk"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 2,
  "email": "staff@hospital.com",
  "role": "hospital_staff"
}
```

---

## Complete Hospital Flow - Step by Step

### STEP 1: Patient Arrives at Hospital
Hospital Staff registers the patient:

```bash
STAFF_TOKEN="<token_from_staff_login>"

curl -X POST "http://localhost:8000/api/staff/patients" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1555555555",
    "blood_group": "O+",
    "gender": "M",
    "date_of_birth": "1990-01-15",
    "address": "123 Main Street, City, State 12345",
    "medical_history": "Allergic to Penicillin, History of Hypertension"
  }'
```

**Response:**
```json
{
  "id": 1,
  "user_id": 3,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1555555555",
  "blood_group": "O+",
  "gender": "M",
  "temporary_password": "abc123XYZ_def",
  "message": "Patient registered successfully. Credentials sent via SMS/Email.",
  "status": "active"
}
```

**What happens:**
- ✅ Patient account created with PATIENT role
- ✅ Patient profile created with medical info
- ✅ Temporary password generated and sent via SMS/Email
- ✅ Patient can now log in with email and temporary password

---

### STEP 2: Hospital Staff Books Appointment

Staff enters patient info and books appointment with doctor:

```bash
curl -X POST "http://localhost:8000/api/staff/appointments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{
    "patient_id": 1,
    "doctor_id": 1,
    "appointment_date": "2026-03-01T14:00:00Z",
    "duration_minutes": 30,
    "chief_complaint": "Chest pain and shortness of breath",
    "symptoms": "Patient experiencing sharp chest pain for 2 days, difficulty breathing, especially when exerting",
    "notes": "Patient walks with difficulty, seems anxious"
  }'
```

**Response:**
```json
{
  "id": 1,
  "appointment_date": "2026-03-01T14:00:00+00:00",
  "status": "scheduled",
  "chief_complaint": "Chest pain and shortness of breath",
  "symptoms": "Patient experiencing sharp chest pain for 2 days, difficulty breathing, especially when exerting",
  "duration_minutes": 30,
  "message": "Appointment created successfully. Notifications sent to patient and doctor."
}
```

**What happens:**
- ✅ Appointment created with status SCHEDULED
- ✅ SMS sent to Patient: "Your appointment confirmed with Dr. Sarah Johnson on March 1 at 2:00 PM..."
- ✅ SMS sent to Doctor: "New appointment: John Doe on March 1 at 2:00 PM. Condition: Chest pain and shortness of breath"
- ✅ Email sent to both
- ✅ In-app notification (if they're using the app)

---

### STEP 3: Patient First Login

Patient receives SMS/Email with credentials:
- **Email:** john.doe@example.com
- **Temporary Password:** abc123XYZ_def

Patient logs in via app or API:

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "abc123XYZ_def"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 3,
  "email": "john.doe@example.com",
  "role": "patient"
}
```

**Required:** Patient must change password on first login:

```bash
PATIENT_TOKEN="<token_from_login>"

curl -X POST "http://localhost:8000/api/auth/change-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PATIENT_TOKEN" \
  -d '{
    "old_password": "abc123XYZ_def",
    "new_password": "MyNewPass456!",
    "confirm_password": "MyNewPass456!"
  }'
```

---

### STEP 4: Patient Views Appointment

Patient can now view their appointment:

```bash
curl -X GET "http://localhost:8000/api/appointments" \
  -H "Authorization: Bearer $PATIENT_TOKEN"
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "doctor_id": 1,
      "doctor_name": "Dr. Sarah Johnson",
      "doctor_specialization": "Cardiology",
      "patient_id": 1,
      "patient_name": "John Doe",
      "patient_email": "john.doe@example.com",
      "appointment_date": "2026-03-01T14:00:00",
      "duration_minutes": 30,
      "status": "scheduled",
      "notes": "Chief Complaint: Chest pain and shortness of breath\nSymptoms: Patient experiencing sharp chest pain for 2 days, difficulty breathing, especially when exerting\nPatient walks with difficulty, seems anxious",
      "reminder_sent": null,
      "created_at": "2026-02-26T10:30:00",
      "updated_at": "2026-02-26T10:30:00"
    }
  ],
  "total": 1
}
```

---

### STEP 5: Doctor Receives Notification

Doctor logs in and views appointment:

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.sarah.johnson@hospital.com",
    "password": "DoctorPass123!"
  }'
```

Doctor views their upcoming appointments:

```bash
DOCTOR_TOKEN="<token_from_login>"

curl -X GET "http://localhost:8000/api/appointments" \
  -H "Authorization: Bearer $DOCTOR_TOKEN"
```

---

### STEP 6: Hospital Staff Views Dashboard

Staff can view all patients and appointments:

```bash
# View all patients
curl -X GET "http://localhost:8000/api/staff/patients?skip=0&limit=10" \
  -H "Authorization: Bearer $STAFF_TOKEN"

# View all appointments
curl -X GET "http://localhost:8000/api/staff/appointments?skip=0&limit=10" \
  -H "Authorization: Bearer $STAFF_TOKEN"

# View dashboard statistics
curl -X GET "http://localhost:8000/api/staff/dashboard-stats" \
  -H "Authorization: Bearer $STAFF_TOKEN"
```

---

## API Endpoint Summary

### Authentication Routes
```
POST   /api/auth/register              - Register user (any role)
POST   /api/auth/login                 - Login
POST   /api/auth/change-password       - Change password
```

### Staff Routes (Staff + Admin)
```
POST   /api/staff/register             - Create staff account (ADMIN ONLY)
POST   /api/staff/patients             - Register patient
POST   /api/staff/appointments         - Book appointment on behalf of patient
GET    /api/staff/patients             - List all patients
GET    /api/staff/appointments         - List all appointments
GET    /api/staff/dashboard-stats      - Dashboard statistics
```

### Patient Routes (Patients)
```
GET    /api/appointments               - View own appointments
POST   /api/appointments               - Book own appointment
```

### Doctor Routes (Doctors)
```
GET    /api/appointments               - View assigned appointments
```

---

## Role Permissions Summary

| Feature | Admin | Staff | Doctor | Patient |
|---------|:-----:|:-----:|:------:|:-------:|
| Create Staff Account | ✅ | ❌ | ❌ | ❌ |
| Register Patient | ✅ | ✅ | ❌ | ❌ (self only) |
| Book Appointment for Patient | ✅ | ✅ | ❌ | ❌ (self only) |
| View All Patients | ✅ | ✅ | ❌ | ❌ |
| View All Appointments | ✅ | ✅ | ❌ (own) | ❌ (own) |
| Dashboard Access | ✅ | ✅ | ❌ | ❌ |

---

## Workflow Diagram

```
┌──────────────────┐
│  Hospital Staff  │
│   (Logs In)      │
└────────┬─────────┘
         │
         ├─► Register New Patient
         │   └─► System sends SMS with credentials
         │
         └─► Book Appointment
             ├─► System creates appointment
             ├─► SMS to Patient: "Appointment confirmed..."
             ├─► SMS to Doctor: "New patient appointment..."
             └─► Email to Both

         ↓

┌──────────────────┐      ┌──────────────────┐      ┌──────────────┐
│      PATIENT     │      │      DOCTOR      │      │     ADMIN    │
│   - Receives     │      │   - Receives     │      │ - Manages    │
│     SMS/Email    │      │     SMS/Email    │      │   Staff      │
│   - First Login  │      │   - Views Info   │      │ - Reports    │
│   - Change Pass  │      │   - Confirms     │      │ - Analytics  │
│   - View Appt    │      │   - Updates      │      └──────────────┘
│   - Update Info  │      │   - Doctor Notes │
└──────────────────┘      └──────────────────┘

         ↓              ↓              ↓

    Day of Appointment
    - Reminders sent (24h, 1h before)
    - Appointment conducted
    - Doctor updates status
    - Following appointment guidance given
```

---

## Testing Checklist

- [ ] Admin can register staff
- [ ] Staff can register patient with all details
- [ ] Patient receives SMS/Email with credentials
- [ ] Staff can book appointment
- [ ] Patient receives SMS notification
- [ ] Doctor receives SMS notification
- [ ] Patient can login with provided credentials
- [ ] Patient must change password on first login
- [ ] Patient can view own appointment
- [ ] Doctor can view patient appointment details
- [ ] Doctor can update appointment notes
- [ ] Staff can view all patients
- [ ] Staff can view all appointments
- [ ] Staff can access dashboard statistics
- [ ] Reminders sent 24h before appointment
- [ ] Reminders sent 1h before appointment
- [ ] Appointment status transitions work correctly
- [ ] Patient can reschedule appointment
- [ ] Patient can cancel appointment

---

## Default Test Credentials (After Setup)

```
ADMIN
  Email: admin@hospital.com
  Password: AdminPass123!
  Role: admin

HOSPITAL_STAFF
  Email: staff@hospital.com
  Password: StaffPass123!
  Role: hospital_staff

DOCTORS (Existing)
  Email: dr.sarah.johnson@hospital.com
  Password: DoctorPass123!
  Role: doctor
  Specialization: Cardiology
  
  Email: dr.james.wilson@hospital.com
  Password: DoctorPass123!
  Role: doctor
  Specialization: Neurology
  
  ... (and more)

PATIENT (Created by Staff)
  Email: john.doe@example.com
  Password: <temporary, must change>
  Role: patient
```

---

## Notifications (Currently Mocked)

### SMS Notifications
- Patient registration credentials
- Appointment confirmation (patient & doctor)
- Appointment reminders (24h, 1h before)
- Appointment cancellation
- Appointment rescheduling

### Email Notifications
- Same as SMS (if configured)

### In-App Notifications
- Real-time alerts when logged in
- Notification history in dashboard

---

## Next Steps for Production

1. **Enable Real SMS:** Integrate Twilio fully
2. **Enable Email:** Configure SMTP settings
3. **Database Backup:** Set up automated backups
4. **Security:** Implement rate limiting, CORS policies
5. **Monitoring:** Add system monitoring and alerts
6. **Logging:** Centralize logs to monitoring service
7. **Frontend UI:** Build Staff Dashboard interface
8. **Mobile App:** Build mobile app for doctors/patients
9. **Analytics:** Add reporting and analytics
10. **Multi-language:** Add i18n support
