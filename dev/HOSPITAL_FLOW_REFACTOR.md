# Hospital Appointment Management System - User Flow & Refactoring

## 1. CURRENT STATE (3 Roles)
```
┌─────────────────────────────────┐
│        USER ROLES               │
├─────────────────────────────────┤
│ • ADMIN (App Developer)         │
│ • DOCTOR (Medical Professional) │
│ • PATIENT (End User)            │
└─────────────────────────────────┘
```

## 2. DESIRED STATE (4 Roles)
```
┌──────────────────────────────────────────┐
│        USER ROLES (UPDATED)              │
├──────────────────────────────────────────┤
│ • ADMIN (App Developer - Super Admin)    │
│ • HOSPITAL_STAFF (Hospital Personnel)    │
│ • DOCTOR (Medical Professional)          │
│ • PATIENT (End User)                     │
└──────────────────────────────────────────┘
```

---

## 3. COMPLETE USER FLOW (Real Hospital Scenario)

### PHASE 1: NEW PATIENT REGISTRATION (Hospital Staff Action)
```
Hospital Staff (Front Desk)
        ↓
    [Login as HOSPITAL_STAFF]
        ↓
    Email: staff@hospital.com
    Password: provided by ADMIN
        ↓
    [Dashboard: Patient Management]
        ↓
    [Register New Patient Button]
        ↓
    Form Fields:
    • Full Name
    • Email
    • Phone Number
    • Date of Birth
    • Gender
    • Blood Group
    • Address
    • Medical History (optional)
        ↓
    [System generates temporary password]
    [Sends credentials to patient via SMS/Email]
        ↓
    Patient Account Created (Status: PATIENT)
    ✅ Notification: Staff → Admin Dashboard
```

### PHASE 2: APPOINTMENT BOOKING (Hospital Staff Action)
```
Hospital Staff (in patient registration form continuation)
        ↓
    [Select Available Doctor from Dropdown]
    [Choose Date & Time]
        ↓
    Form Fields:
    • Disease/Chief Complaint
    • Symptoms
    • Medical History relevant to visit
    • Contact Number (verify)
    • Preferred Doctor (if any)
    • Appointment Reason
        ↓
    [System checks Doctor's Availability]
    [System checks for Conflicts]
        ↓
    [Book Appointment Button]
        ↓
    Appointment Created (Status: SCHEDULED)
        ↓
    ✅ NOTIFICATIONS TRIGGERED:
    
    a) SMS to Patient:
       "Your appointment confirmed with Dr. [Name]
        on [Date] at [Time]. Contact: [Hospital]"
    
    b) SMS to Doctor:
       "New appointment: [Patient Name]
        on [Date] at [Time]. Condition: [Disease]"
    
    c) Email to Both
    
    d) In-App Notification (if app is open)
```

### PHASE 3: PATIENT VERIFICATION (Patient Action)
```
Patient receives SMS/Email with credentials
        ↓
    [Download App]
    [Login as PATIENT]
        ↓
    Email: (provided by staff)
    Password: (provided by staff)
        ↓
    First Login: MUST CHANGE PASSWORD
        ↓
    [View Dashboard]
    ├── My Appointments (Scheduled)
    ├── My Medical Records
    ├── Doctor Details
    └── View Appointment Details
        ↓
    Can Reschedule/Cancel Appointment
    ✅ Doctor gets notified of changes
```

### PHASE 4: DOCTOR RECEIVES NOTIFICATION (Doctor Action)
```
Doctor receives SMS notification
        ↓
    [Doctor opens App/Dashboard]
    [Login as DOCTOR]
        ↓
    Email: dr.name@hospital.com
    Password: DoctorPass123!
        ↓
    [View Upcoming Appointments]
    ├── Today's Schedule
    ├── This Week's Schedule
    └── View Patient Details
        ↓
    [View Patient Info]
    ├── Medical History
    ├── Previous Records
    ├── Chief Complaint
    └── Contact Number
        ↓
    [Accept/Confirm Appointment]
    [Add Medical Notes (optional)]
        ↓
    Patient gets notification of confirmation
```

### PHASE 5: APPOINTMENT DAY
```
System sends reminder notifications:

1. 24 hours before:
   Patient SMS: "Appointment reminder: Tomorrow at [Time]"
   Doctor SMS: "Appointment tomorrow: [Patient Name] at [Time]"

2. 1 hour before:
   Patient SMS: "Appointment in 1 hour at [Hospital]"
   Doctor SMS: "Appointment starting soon"

3. Appointment Completion:
   [Doctor marks appointment as COMPLETED]
   [Doctor adds medical notes]
   [Patient receives link to book follow-up]
```

---

## 4. ROLE-BASED PERMISSIONS MATRIX

| Action | Patient | Doctor | Staff | Admin |
|--------|---------|--------|-------|-------|
| View Own Appointments | ✅ | ✅ | ❌ | ❌ |
| Book Appointment (self) | ✅ | ❌ | ❌ | ❌ |
| Book Appointment (for patient) | ❌ | ❌ | ✅ | ✅ |
| Register Patient (self) | ❌ | ✅ | ❌ | ❌ |
| Register Patient (for others) | ❌ | ❌ | ✅ | ✅ |
| View All Appointments | ❌ | ✅ (own) | ✅ | ✅ |
| View All Patients | ❌ | ❌ | ✅ | ✅ |
| View All Doctors | ✅ | ❌ | ✅ | ✅ |
| Manage Hospital Staff | ❌ | ❌ | ❌ | ✅ |
| View System Reports | ❌ | ❌ | ✅ | ✅ |
| Manage Database | ❌ | ❌ | ❌ | ✅ |

---

## 5. CODE CHANGES REQUIRED

### 5.1 Database Models
- ✅ Update `UserRole` enum to include `HOSPITAL_STAFF`
- ✅ No schema changes needed (use existing User model)

### 5.2 Authentication
- ✅ Update registration to accept HOSPITAL_STAFF role
- ✅ Add role-based authorization decorators

### 5.3 API Routes
```
PATIENT Routes:
  GET    /api/appointments           - View own appointments
  POST   /api/appointments           - Book appointment
  PUT    /api/appointments/{id}      - Reschedule
  DELETE /api/appointments/{id}      - Cancel

DOCTOR Routes:
  GET    /api/appointments           - View assigned appointments
  PUT    /api/appointments/{id}      - Update status/notes
  GET    /api/patients               - View assigned patients

HOSPITAL_STAFF Routes:
  POST   /api/patients               - Register new patient
  POST   /api/appointments           - Book on behalf of patient
  GET    /api/patients               - View all patients
  GET    /api/appointments           - View all appointments
  GET    /api/staff/reports          - Generate reports

ADMIN Routes:
  All of the above +
  POST   /api/staff                  - Create staff accounts
  GET    /api/staff                  - Manage staff
  GET    /api/admin/dashboard        - System overview
```

### 5.4 Notifications
- ✅ Appointment Created → Notify Patient + Doctor
- ✅ Appointment Updated → Notify Patient + Doctor
- ✅ Appointment Cancelled → Notify Patient + Doctor
- ✅ Reminder 24h before → Notify Patient + Doctor
- ✅ Reminder 1h before → Notify Patient + Doctor

---

## 6. IMPLEMENTATION ROADMAP

### STEP 1: Update Database Models
- Add `HOSPITAL_STAFF` to `UserRole` enum

### STEP 2: Create New Schemas
- `StaffRegisterRequest` - ADMIN creates staff account
- `PatientRegisterByStaffRequest` - Staff registers patient
- `AppointmentCreateByStaffRequest` - Staff books appointment
- Separate schemas for each role's appointment creation

### STEP 3: Create Authorization Decorators
- `@require_admin` - Admin only
- `@require_staff` - Staff or Admin
- `@require_doctor` - Doctor only
- `@require_patient` - Patient only

### STEP 4: Update Routes
Create new route files:
- `/api/staff/` - Staff management (Admin only)
- `/api/patients/` - Patient management (Staff + Admin)
- Update appointment routes for staff creation

### STEP 5: Update Services
- `PatientService` - Add patient registration by staff
- `AppointmentService` - Add appointment creation by staff
- `StaffService` - New service for staff management

### STEP 6: Update Frontend Routes
- Staff Login Page
- Staff Dashboard (Patient Management)
- Staff Appointment Booking Interface
- Admin Dashboard (Staff Management)

### STEP 7: Testing
- Create test staff account setup script
- Create flow test scripts
- Integration testing

---

## 7. LOGIN CREDENTIALS AFTER REFACTORING

```
ADMIN (App Developer - Created by Migration)
├─ Email: admin@hospital.com
├─ Password: AdminPass123!
└─ Access: Everything

HOSPITAL_STAFF (Created by Admin)
├─ Email: staff@hospital.com
├─ Password: StaffPass123!
└─ Access: Patient management, Appointment booking, Reports

DOCTORS (Existing)
├─ Email: dr.sarah.johnson@hospital.com
├─ Password: DoctorPass123!
└─ Access: Own appointments, Patient records

PATIENTS (New or Self-Registered)
├─ Email: patient@example.com
├─ Password: (Own password)
└─ Access: Own appointments, own records
```

---

## 8. CURRENT WORKING FLOW (Unchanged)

```
1. Patient registers directly via app ✅
2. Patient books appointment ✅
3. Doctor receives notification ✅
4. Both get notifications ✅
```

## NEW FLOW (To Implement)

```
1. Hospital Staff registers patient ✅ (NEW)
2. Hospital Staff books appointment on behalf ✅ (NEW)
3. Patient receives credentials via SMS ✅ (NEW)
4. Patient verifies and changes password ✅ (NEW)
5. Doctor receives notification ✅ (EXISTING)
6. Both get notifications ✅ (EXISTING)
7. Admin manages staff accounts ✅ (NEW)
```

---

## 9. DEPLOYMENT STRATEGY

1. Add migration to create HOSPITAL_STAFF role
2. Add migration to create default ADMIN account
3. Update authentication routes
4. Update appointment routes
5. Create staff management routes
6. Update frontend components
7. Run integration tests
8. Deploy to production
