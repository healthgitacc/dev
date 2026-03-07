# ⚡ Quick Start - Run Your Application

## **One-Line Commands to Start Everything**

### **Terminal 1: Start Backend**
```powershell
cd "e:\project\POC 1st\backend" ; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Terminal 2: Start Frontend**
```powershell
cd "e:\project\POC 1st\frontend" ; npm run dev
```

---

## **Access Your Application**

| Component | URL |
|-----------|-----|
| **Frontend Web App** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Documentation** | http://localhost:8000/docs |
| **Alternative Docs** | http://localhost:8000/redoc |
| **Health Check** | http://localhost:8000/health |

---

## **Login Credentials**

### **Create Super Admin (First Time)**

Go to http://localhost:8000/docs and use the **`/api/auth/register`** endpoint:

```json
{
  "name": "App Owner",
  "email": "super@hospital.com",
  "password": "SuperAdmin123!",
  "phone": "+1234567890",
  "role": "super_admin"
}
```

### **Hospital Admin Registration**

Use Super Admin token → **`POST /api/admin/create-hospital-admin`**:

```json
{
  "name": "Hospital Manager",
  "email": "admin@hospital.com",
  "password": "HospitalAdmin123!",
  "phone": "+1234567890"
}
```

---

## **Test the Flow**

### **Step 1: Login as Hospital Admin**
```
POST /api/auth/login
{
  "email": "admin@hospital.com",
  "password": "HospitalAdmin123!"
}
```

### **Step 2: Add a Patient**
```
POST /api/staff/patients
{
  "name": "John Patient",
  "email": "john@patient.com",
  "phone": "+1111111111",
  "blood_group": "O+",
  "gender": "M",
  "date_of_birth": "1990-01-15",
  "address": "123 Main St",
  "medical_history": "None"
}
```
✅ **Patient receives SMS with temporary password**

### **Step 3: Add a Doctor**
```
POST /api/staff/doctors
{
  "name": "Dr. Sarah",
  "email": "dr.sarah@hospital.com",
  "phone": "+2222222222",
  "specialization": "Cardiology",
  "experience_years": 10,
  "license_number": "MD-001"
}
```
✅ **Doctor receives SMS with credentials**

### **Step 4: Book Appointment**
```
POST /api/staff/appointments
{
  "patient_id": 1,
  "doctor_id": 1,
  "appointment_datetime": "2026-03-15T14:30:00",
  "reason": "Checkup"
}
```
✅ **Both patient and doctor receive SMS alerts**

---

## **New System Rules**

### **Hospital Admin CAN:**
- ✅ Add patients
- ✅ Add doctors  
- ✅ Book appointments
- ✅ View appointment schedule

### **Hospital Admin CANNOT (Privacy Policy):**
- ❌ View patient details
- ❌ View doctor details
- ❌ See medical history
- ❌ Approve hospitals

---

## **Troubleshooting**

### **Backend won't start?**
```powershell
# Kill any process using port 8000
netstat -ano | findstr ":8000"
taskkill /PID <number> /F

# Then try again
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **Frontend won't start?**
```powershell
cd "e:\project\POC 1st\frontend"
rm -r node_modules  # or remove node_modules folder manually
npm install
npm run dev
```

### **Database error?**
```powershell
cd "e:\project\POC 1st"
del hospital.db
# Restart backend - it creates new database
```

---

## **Key Files Updated**

✅ `backend/app/core/auth.py` - Role-based access control (Super Admin vs Hospital Admin)  
✅ `backend/app/routes/patient_routes.py` - Hospital admin cannot view patient details  
✅ `backend/app/routes/doctor_routes.py` - Hospital admin privacy restrictions  
✅ `backend/app/routes/staff_routes.py` - Hospital admin operations  
✅ `frontend/next.config.js` - Fixed configuration  

---

## **Documentation Files**

📄 **STARTUP_GUIDE.md** - Complete startup and workflow guide  
📄 **REFACTORED_FLOW.md** - Detailed architecture and role definitions  
📄 **QUICK_START.md** - This file (quick reference)  

---

## **System Status**

✅ Backend running on port 8000  
✅ Frontend running on port 3000  
✅ SQLite database connected  
✅ SMS notification system ready  
✅ Appointment reminder scheduler active  
✅ Role-based access control enforced  
✅ Privacy policy implemented  

---

**Ready to run!** 🚀

Just copy the commands above into two separate PowerShell terminals and you're good to go!
