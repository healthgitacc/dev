# Hospital Management System - Database Schema

## Overview

The hospital management system database consists of **6 main tables** that work together to manage users, medical professionals, patients, appointments, and medical records.

---

## Database Tables

### 1. **users** (Core User Management)

**Purpose:** Stores all user accounts with authentication and role-based access control

**Table Structure:**
```sql
users (
  id: INTEGER (primary key)
  name: VARCHAR(255) - User's full name
  email: VARCHAR(255) - Unique email for login
  phone: VARCHAR(20) - Contact number
  password_hash: VARCHAR(255) - Encrypted password
  role: STRING(50) - User type (super_admin, hospital_admin, doctor, patient)
  is_active: BOOLEAN - Account status (default: true)
  created_at: TIMESTAMP - Account creation time
  updated_at: TIMESTAMP - Last update time
)
```

**Key Columns:**
- `id` - Primary key, unique identifier
- `email` - Unique, indexed for quick login lookups
- `role` - Enum values: `super_admin`, `hospital_admin`, `doctor`, `patient`
- `is_active` - Can deactivate accounts without deleting

**Use Case:** Base table for all system users. Every doctor and patient must have a user account for authentication and authorization.

**Indexes:**
- `idx_users_email` - Fast email lookups (login, password recovery)
- `idx_users_role` - Quick role-based queries
- `idx_users_created_at` - Timeline queries

**Relationships:**
- One-to-One with `doctors` table (via user_id)
- One-to-One with `patients` table (via user_id)

---

### 2. **doctors** (Medical Professional Profiles)

**Purpose:** Extends user data with medical qualifications and specialization information

**Table Structure:**
```sql
doctors (
  id: INTEGER (primary key)
  user_id: INTEGER (foreign key → users.id, unique)
  specialization: VARCHAR(255) - Medical specialty
  experience_years: INTEGER - Years of practice
  license_number: VARCHAR(100) - Medical license identifier
  created_at: TIMESTAMP - Profile creation time
  updated_at: TIMESTAMP - Last update time
)
```

**Key Columns:**
- `id` - Primary key
- `user_id` - Foreign key to users table (one-to-one, cascade delete)
- `specialization` - Examples: Cardiology, Neurology, Pediatrics, General Practice, etc.
- `experience_years` - Integer representing years of medical practice
- `license_number` - Unique identifier for medical license

**Current Specializations in System:**
- Cardiology (12 years)
- Endocrinology (10 years)
- General Practice (8 years)
- Neurology (14 years)
- Orthopedics (11 years)
- Psychiatry (9 years)
- Pediatrics (7 years)
- Dermatology (13 years)
- Ophthalmology (10 years)
- ENT (11 years)

**Use Case:** 
- Patient can filter and book appointments by doctor specialty
- Admin can view doctor qualifications and experience
- Generate reports on doctor specialization distribution

**Indexes:**
- `idx_doctors_user_id` - Link to user profile
- `idx_doctors_specialization` - Filter doctors by specialty
- `idx_doctors_license_number` - Verify unique license numbers

**Relationships:**
- One-to-One with `users` table (doctor user profile)
- One-to-Many with `appointments` table (doctor-patient meetings)
- One-to-Many with `medical_records` table (records created by doctor)

---

### 3. **patients** (Patient Medical Information)

**Purpose:** Extends user data with patient health details and demographics

**Table Structure:**
```sql
patients (
  id: INTEGER (primary key)
  user_id: INTEGER (foreign key → users.id, unique)
  age: INTEGER - Patient age
  gender: VARCHAR(10) - Gender (male, female, other)
  blood_group: VARCHAR(5) - Blood type (O+, O-, A+, A-, B+, B-, AB+, AB-)
  medical_history: VARCHAR(500) - Previous medical conditions/notes
  created_at: TIMESTAMP - Profile creation time
  updated_at: TIMESTAMP - Last update time
)
```

**Key Columns:**
- `id` - Primary key
- `user_id` - Foreign key to users table (one-to-one, cascade delete)
- `age` - Patient age
- `gender` - Enum-like: "male", "female", "other"
- `blood_group` - Blood type for medical emergencies
- `medical_history` - Text field for past conditions, allergies, etc.

**Use Case:**
- Store patient demographics and health history
- Blood group used in emergency situations
- Medical history helps doctors understand patient background
- Age-based filtering for health recommendations

**Indexes:**
- `idx_patients_user_id` - Link to user profile
- `idx_patients_gender` - Demographic queries

**Relationships:**
- One-to-One with `users` table (patient user profile)
- One-to-Many with `appointments` table (patient's scheduled appointments)
- One-to-Many with `medical_records` table (patient's medical history)

---

### 4. **appointments** (Booking & Scheduling)

**Purpose:** Records all patient appointments with doctors, tracking status and details

**Table Structure:**
```sql
appointments (
  id: INTEGER (primary key)
  doctor_id: INTEGER (foreign key → doctors.id)
  patient_id: INTEGER (foreign key → patients.id)
  appointment_date: TIMESTAMP - Scheduled date/time
  duration_minutes: INTEGER - Duration (typically 30 minutes)
  status: STRING - scheduled, completed, cancelled, no_show, rescheduled
  notes: TEXT - Appointment notes/chief complaint
  reminder_sent: TIMESTAMP - When SMS reminder was sent
  created_at: TIMESTAMP - Booking creation time
  updated_at: TIMESTAMP - Last update time
)
```

**Key Columns:**
- `id` - Primary key
- `doctor_id` - Foreign key to doctors table
- `patient_id` - Foreign key to patients table
- `appointment_date` - DateTime of scheduled appointment
- `duration_minutes` - Length of appointment (standard: 30 minutes)
- `status` - Current appointment state
  - `scheduled` - Confirmed, waiting for appointment time
  - `completed` - Appointment finished, medical record created
  - `cancelled` - Patient or doctor cancelled
  - `no_show` - Patient didn't show up
  - `rescheduled` - Moved to different time
- `notes` - Chief complaint or appointment description
- `reminder_sent` - Timestamp of SMS notification sent

**Use Case:**
- Central hub for appointment management
- Track all doctor-patient meetings
- Enable SMS reminders (sent when reminder_sent is null)
- Filter appointments by status for reporting
- Support appointment cancellation and completion workflows

**Indexes:**
- `idx_appointments_doctor_id` - Get doctor's appointments
- `idx_appointments_patient_id` - Get patient's appointments
- `idx_appointments_date` - Find appointments by date range
- `idx_appointments_status` - Filter by status
- `idx_appointments_doctor_date` - Combined queries (doctor's appointments on specific date)

**Relationships:**
- Many-to-One with `doctors` table
- Many-to-One with `patients` table
- One-to-Many with `medical_records` table (follow-up records after appointment)

---

### 5. **medical_records** (Patient Health Records)

**Purpose:** Documents patient diagnoses, treatments, and clinical notes from doctor visits

**Table Structure:**
```sql
medical_records (
  id: INTEGER (primary key)
  patient_id: INTEGER (foreign key → patients.id)
  doctor_id: INTEGER (foreign key → doctors.id, nullable)
  disease_name: VARCHAR(255) - Diagnosis/condition name
  diagnosis: TEXT - Detailed diagnosis description
  prescription_text: TEXT - Prescribed medications
  dosage: VARCHAR(255) - Medication dosage instructions
  follow_up_date: TIMESTAMP - Date for next visit
  notes: TEXT - Additional medical notes
  created_at: TIMESTAMP - Record creation time
  updated_at: TIMESTAMP - Last update time
)
```

**Key Columns:**
- `id` - Primary key
- `patient_id` - Foreign key to patients table
- `doctor_id` - Foreign key to doctors table (nullable if doctor account deleted)
- `disease_name` - Primary condition (e.g., "Hypertension", "Type 2 Diabetes")
- `diagnosis` - Detailed clinical findings
- `prescription_text` - Medications prescribed
- `dosage` - How to take medications (e.g., "2 tablets twice daily with food")
- `follow_up_date` - When patient should return for follow-up
- `notes` - Additional clinical information, observations, warnings

**Use Case:**
- Maintain patient's medical history
- Provide continuity of care (doctors can see past diagnoses)
- Track prescribed medications
- Enable medical report generation and download
- Schedule follow-up appointments based on clinical needs

**Indexes:**
- `idx_medical_records_patient_id` - Get patient's medical history
- `idx_medical_records_doctor_id` - Get records created by specific doctor
- `idx_medical_records_created_at` - Timeline queries
- `idx_medical_records_follow_up_date` - Find overdue follow-ups

**Relationships:**
- Many-to-One with `patients` table
- Many-to-One with `doctors` table

---

## Database Relationships Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      users (5)                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ id, name, email, phone, password_hash,           │   │
│  │ role (super_admin/hospital_admin/doctor/patient),│   │
│  │ is_active, created_at, updated_at                │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
    ┌──────────────┐    ┌──────────────┐
    │   doctors    │    │   patients   │
    │  (1:1 with   │    │  (1:1 with   │
    │   users)     │    │   users)     │
    └──────────────┘    └──────────────┘
          │ (1)               │ (1)
          │                   │
          │ (many)            │ (many)
          └─────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │  appointments    │
           │ (doctor-patient  │
           │  meetings)       │
           └──────────────────┘
                    │
                    │ (1)
                    │
                    ▼ (many)
           ┌──────────────────────┐
           │  medical_records     │
           │ (health history,     │
           │  diagnoses)          │
           └──────────────────────┘
```

## Relationship Summary

| Relationship | Cardinality | Details |
|---|---|---|
| **User → Doctor** | 1:1 | One doctor user has one doctor profile |
| **User → Patient** | 1:1 | One patient user has one patient profile |
| **Doctor → Appointments** | 1:N | One doctor has many appointments |
| **Patient → Appointments** | 1:N | One patient has many appointments |
| **Doctor ← Appointment → Patient** | N:N | Many-to-many through appointments |
| **Appointment → Medical Records** | 1:N | One appointment can have multiple follow-up records |
| **Doctor → Medical Records** | 1:N | One doctor creates many medical records |
| **Patient → Medical Records** | 1:N | One patient has many medical records |

---

## Data Flow Examples

### Example 1: Patient Books Appointment
```
1. Patient signs up/logs in → User created with role='patient'
2. Patient record created → Stores age, gender, blood group
3. Patient selects doctor → Doctor record shows specialization, experience
4. Patient books slot → Appointment created (status='scheduled')
5. SMS reminder sent → reminder_sent timestamp updated
6. Doctor completes visit → Appointment status changed to 'completed'
```

### Example 2: Doctor Creates Medical Record
```
1. Patient visits doctor (appointment status='scheduled')
2. Doctor examines patient
3. Doctor creates medical record:
   - disease_name: "Type 2 Diabetes"
   - diagnosis: "Elevated blood glucose levels..."
   - prescription_text: "Metformin 500mg"
   - dosage: "Twice daily after meals"
   - follow_up_date: "2026-04-05" (30 days later)
4. Appointment status changed to 'completed'
5. Patient can download medical report from medical-records page
```

### Example 3: Hospital Admin Books for Patient
```
1. Admin enters patient details (name, email, phone)
2. System creates/finds patient record
3. Admin selects doctor and appointment time
4. Appointment created with SMS notifications sent
5. Doctor can view patient history before meeting
6. After appointment, medical record created
```

---

## Current Database State

### Doctors in System: 14
```
Total Doctors: 14
Specializations: 10 unique specializations
Experience Range: 7-14 years
Doctor Fields Populated: name, specialization, experience_years, license_number
```

### Appointment Status Distribution
- scheduled: Active upcoming appointments
- completed: Finished appointments with medical records
- cancelled: Cancelled by patient/doctor
- no_show: Patient missed appointment
- rescheduled: Moved to different time

### SMS Notifications
- Appointment booking: Confirmation SMS
- Appointment reminder: Sent before appointment (configurable timing)
- Appointment cancellation: Different message format with cancellation details

---

## Key Features Enabled by Schema

1. **Role-Based Access Control**
   - Super Admin: Full system control
   - Hospital Admin: Manage appointments and patients
   - Doctor: View and complete appointments
   - Patient: Book and view own appointments

2. **Appointment Management**
   - Book appointments with specific doctors
   - View available doctors by specialization
   - Track appointment status (scheduled, completed, cancelled, etc.)
   - Receive SMS reminders

3. **Medical Records**
   - Create records after appointments
   - Store diagnoses and prescriptions
   - Schedule follow-up appointments
   - Download medical reports as PDF/TXT

4. **User Management**
   - Patient registration and profiles
   - Doctor profiles with specialization
   - Audit trail with created_at, updated_at timestamps

5. **Reporting & Analytics**
   - Dashboard statistics (total appointments, completed, cancelled)
   - Doctor availability and workload
   - Patient medical history timeline
   - Follow-up tracking for patient care

---

## Database Constraints & Validations

### Foreign Key Constraints
- `doctors.user_id` → `users.id` (CASCADE DELETE)
- `patients.user_id` → `users.id` (CASCADE DELETE)
- `appointments.doctor_id` → `doctors.id` (CASCADE DELETE)
- `appointments.patient_id` → `patients.id` (CASCADE DELETE)
- `medical_records.patient_id` → `patients.id` (CASCADE DELETE)
- `medical_records.doctor_id` → `doctors.id` (SET NULL for historical records)

### Unique Constraints
- `users.email` - No duplicate email addresses
- `doctors.user_id` - Each user can have at most one doctor profile
- `doctors.license_number` - No duplicate medical licenses
- `patients.user_id` - Each user can have at most one patient profile

### Required Fields
- **users**: name, email, password_hash, role
- **doctors**: user_id, specialization, experience_years
- **patients**: user_id
- **appointments**: doctor_id, patient_id, appointment_date, duration_minutes
- **medical_records**: patient_id, disease_name, diagnosis

---

## Performance Considerations

### Indexes for Fast Queries
- Email-based user lookups
- Role-based filtering
- Doctor specialization searches
- Appointment date range queries
- Patient history retrieval
- Follow-up date searches

### Cascade Delete Strategy
- Deleting a user cascades to doctor/patient profiles
- Deleting a doctor cascades to their appointments
- Medical records maintain doctor reference for historical accuracy

### Query Optimization
- Use indexed columns for WHERE clauses
- Combine doctor+date index for availability checks
- Pre-filter by status before fetching appointment details
