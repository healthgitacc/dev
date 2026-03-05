# 🚀 Hospital Management System - Startup Guide

## **Quick Start Commands**

### **1. Start Backend (FastAPI + SQLite)**

```bash
cd "e:\project\POC 1st\backend"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend will be available at:**
- API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

### **2. Start Frontend (Next.js)**

```bash
cd "e:\project\POC 1st\frontend"
npm run dev
```

**Frontend will be available at:**
- Web App: `http://localhost:3000`

---

## **New Role-Based Access System**

### 🔑 **System Architecture**

Only **2 Login Types**:

#### **1. Super Admin (Application Owner)**
- **Permissions:**
  - ✅ Approve hospital registration requests
  - ✅ Activate/Deactivate hospitals
  - ✅ Manage system-wide settings
  - ✅ Access analytics dashboard
  - ❌ Cannot see patient/doctor details (security)

- **Use Case:** App owner/company administrator

---

#### **2. Hospital Admin**
- **Permissions:**
  - ✅ Add new patients to hospital
  - ✅ Add new doctors to hospital
  - ✅ Book appointments for patients
  - ✅ View appointment schedule
  - ❌ Cannot view patient details (privacy policy)
  - ❌ Cannot view doctor details (privacy policy)
  - ❌ Cannot approve hospitals

- **Use Case:** Hospital receptionist/manager

---

#### **3. Patient (No Login Needed for Initial)**
- **Receives:**
  - 📱 SMS alert when registered
  - 📱 SMS alert when appointment is booked
  - ✅ Can view own profile
  - ❌ Cannot view other patients
  - ❌ Cannot view doctors (except when appointment reminder)

- **Use Case:** Hospital patient

---

#### **4. Doctor (No Login Needed for Initial)**
- **Receives:**
  - 📱 SMS alert when registered
  - 📱 SMS alert when appointment is booked
  - ✅ Can view own profile
  - ✅ Can view their appointments
  - ❌ Cannot view other doctors
  - ❌ Cannot view patient details (view only during appointment)

- **Use Case:** Hospital doctor

---

## **Test Credentials**

### **Super Admin Login**
```
Email:    super@hospital.com
Password: SuperAdmin123!
Role:     super_admin
```

**To Create Super Admin (first time):**
Use the registration endpoint:

```bash
POST /api/auth/register

{
  "name": "System Owner",
  "email": "super@hospital.com",
  "password": "SuperAdmin123!",
  "role": "super_admin"
}
```

---

### **Hospital Admin Login**
```
Email:    admin@hospital.com
Password: HospitalAdmin123!
Role:     hospital_admin
```

**To Create Hospital Admin:**
- Super Admin must register them via: `POST /api/staff/admins`

---

### **Sample Patient for Testing**
```
Email:    patient@hospital.com
Password: Patient123!
Role:     patient
```

---

## **API Workflow**

### **Flow 1: Hospital Setup (Super Admin)**

1. **Super Admin Login**
   ```bash
   POST /api/auth/login
   {
     "email": "super@hospital.com",
     "password": "SuperAdmin123!"
   }
   ```

2. **Register Hospital Admin**
   ```bash
   POST /api/staff/admins
   Header: Authorization: Bearer <super_admin_token>
   
   {
     "name": "Admin Name",
     "email": "admin@hospital.com",
     "password": "HospitalAdmin123!"
   }
   ```

3. **Send Hospital Activation SMS**
   - Automatic SMS sent to admin's phone

---

### **Flow 2: Patient Registration (Hospital Admin)**

1. **Hospital Admin Login**
   ```bash
   POST /api/auth/login
   {
     "email": "admin@hospital.com",
     "password": "HospitalAdmin123!"
   }
   ```

2. **Add Patient**
   ```bash
   POST /api/staff/patients
   Header: Authorization: Bearer <hospital_admin_token>
   
   {
     "name": "Patient Name",
     "email": "patient@hospital.com",
     "phone": "+1234567890",
     "blood_group": "O+",
     "gender": "M",
     "date_of_birth": "1995-01-15",
     "address": "123 Main St",
     "medical_history": "None"
   }
   ```

3. **Patient Receives SMS**
   - Temporary password sent via SMS
   - Patient can login with password to change it

---

### **Flow 3: Book Appointment (Hospital Admin)**

1. **Add Doctor (First)**
   ```bash
   POST /api/staff/doctors
   Header: Authorization: Bearer <hospital_admin_token>
   
   {
     "name": "Dr. Smith",
     "email": "dr.smith@hospital.com",
     "phone": "555-0001",
     "specialization": "Cardiology",
     "experience_years": 10,
     "license_number": "MD-001"
   }
   ```

2. **Book Appointment**
   ```bash
   POST /api/staff/appointments
   Header: Authorization: Bearer <hospital_admin_token>
   
   {
     "patient_id": 1,
     "doctor_id": 1,
     "appointment_datetime": "2026-03-15T14:30:00",
     "reason": "Regular checkup"
   }
   ```

3. **SMS Alerts Sent**
   - ✅ Patient receives appointment notification
   - ✅ Doctor receives appointment notification

---

## **Privacy & Security Rules**

✅ **What Hospital Admin CAN see:**
- Hospital appointments schedule
- Operation status
- Patient list (names only, for selection)
- Doctor list (names only, for selection)

❌ **What Hospital Admin CANNOT see:**
- Patient medical history
- Patient phone/email
- Doctor credentials
- Past medical records
- Any detailed personal information

✅ **What Patients/Doctors CAN see:**
- Only their own information
- Their own appointments

---

## **Troubleshooting**

### **Port Already in Use**
If port 8000 or 3000 is in use:

```bash
# Find process using port 8000
netstat -ano | findstr "8000"

# Kill process (replace PID with actual number)
taskkill /PID <PID> /F
```

### **Database Reset**
To clear all data and restart:

```bash
cd "e:\project\POC 1st\backend"
# Delete hospital.db file
del hospital.db

# Restart backend - it will recreate the database
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **Frontend Not Loading**
```bash
cd "e:\project\POC 1st\frontend"
del node_modules (entire folder)
npm install
npm run dev
```

---

## **Files Modified for New Flow**

✅ Updated auth.py - Role-based access control
✅ Updated patient_routes.py - Hospital admin privacy restrictions
✅ Updated doctor_routes.py - Hospital admin privacy restrictions
✅ Updated staff_routes.py - Hospital admin operations

---

## **Next Steps**

1. ✅ Run backend: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
2. ✅ Run frontend: `npm run dev`
3. ✅ Create Super Admin account
4. ✅ Create Hospital Admin account
5. ✅ Test patient registration and appointment booking

---

**All set! Your system is ready to manage hospitals with proper privacy controls.** 🏥
