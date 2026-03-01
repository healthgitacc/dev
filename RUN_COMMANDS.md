# 🎯 COPY-PASTE COMMANDS - Start Your Application

## **Option 1: Windows PowerShell (Simplest)**

### **Open PowerShell Terminal 1**
```powershell
cd "e:\project\POC 1st\backend"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Open PowerShell Terminal 2**
```powershell
cd "e:\project\POC 1st\frontend"
npm run dev
```

**Done! Your app will be ready in ~30 seconds.**

---

## **Option 2: One Combined Command (If you want both terminals)**

```powershell
# Run in ONE terminal (both run simultaneously)
cd "e:\project\POC 1st"; Start-Process -NoNewWindow powershell -ArgumentList '-NoExit -Command cd "e:\project\POC 1st\backend"; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload'; cd "e:\project\POC 1st\frontend"; npm run dev
```

---

## **Option 3: Using VS Code Terminal**

[Open VS Code, go to Terminal > New Terminal]

```
Terminal 1:
> cd "e:\project\POC 1st\backend"
> uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Terminal 2:
> cd "e:\project\POC 1st\frontend"
> npm run dev
```

---

## **Then Access Your Application**

✅ **Frontend Web App:** http://localhost:3000  
✅ **Backend API:** http://localhost:8000  
✅ **API Docs:** http://localhost:8000/docs  
✅ **Health Check:** http://localhost:8000/health  

---

## **First Time Setup (Do This Once)**

### **Create Super Admin**

Go to: http://localhost:8000/docs

Find: **`POST /api/auth/register`**

Copy-paste this JSON:

```json
{
  "name": "System Owner",
  "email": "super@hospital.com",
  "password": "SuperAdmin123!",
  "phone": "+1234567890",
  "role": "super_admin"
}
```

✅ **Done! Now you can login in Swagger**

---

## **Then Create Hospital Admin**

Still in Swagger: http://localhost:8000/docs

Find: **`POST /api/admin/create-hospital-admin`**

1. Click the "Authorize" button (lock icon top-right)
2. Paste your Super Admin token from login
3. Paste this JSON:

```json
{
  "name": "Hospital Manager",
  "email": "admin@hospital.com",
  "password": "HospitalAdmin123!",
  "phone": "+1111111111"
}
```

✅ **Hospital Admin created! Can now add patients and doctors.**

---

## **Quick Test Flow**

### **1. Login as Hospital Admin**

Endpoint: **`POST /api/auth/login`**

```json
{
  "email": "admin@hospital.com",
  "password": "HospitalAdmin123!"
}
```

Save the `access_token` from response.

---

### **2. Add Patient**

Endpoint: **`POST /api/staff/patients`**

Add auth token first:
- Click "Authorize" button
- Paste: `Bearer <your_token_here>`

Then use this JSON:

```json
{
  "name": "John Patient",
  "email": "john@patient.com",
  "phone": "+1234567890",
  "blood_group": "O+",
  "gender": "M",
  "date_of_birth": "1990-01-15",
  "address": "123 Main St",
  "medical_history": "None"
}
```

✅ **Patient added! John receives SMS with temp password**

---

### **3. Add Doctor**

Endpoint: **`POST /api/staff/doctors`**

(Same auth token as above)

```json
{
  "name": "Dr. Sarah Johnson",
  "email": "dr.sarah@hospital.com",
  "phone": "+2222222222",
  "specialization": "Cardiology",
  "experience_years": 10,
  "license_number": "MD-001"
}
```

✅ **Doctor added! Sarah receives SMS with credentials**

---

### **4. Book Appointment**

Endpoint: **`POST /api/staff/appointments`**

(Same auth token)

```json
{
  "patient_id": 1,
  "doctor_id": 1,
  "appointment_datetime": "2026-03-15T14:30:00",
  "reason": "Regular checkup"
}
```

✅ **Appointment booked! Both John and Sarah receive SMS!**

---

## **Test Role-Based Privacy**

Try this to confirm privacy is working:

Endpoint: **`GET /api/patients`** (as Hospital Admin)

Expected: **403 Forbidden**

Message: `"Hospital admin cannot view patient details (privacy policy)"`

✅ **This is correct! Privacy protection is working.**

---

## **Kill Process (If Something Gets Stuck)**

```powershell
# Find what's using port 8000
netstat -ano | findstr ":8000"

# Kill it (replace 12345 with actual PID)
taskkill /PID 12345 /F

# Find what's using port 3000
netstat -ano | findstr ":3000"

# Kill it
taskkill /PID 54321 /F
```

---

## **Reset Database**

```powershell
cd "e:\project\POC 1st"
del hospital.db

# Restart backend - it recreates the database
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## **Minimal Troubleshooting**

| Issue | Solution |
|-------|----------|
| Backend won't start | `taskkill /PID <number> /F` then try again |
| Frontend won't start | Delete `node_modules` and run `npm install` |
| Can't connect | Make sure both are running on 8000 and 3000 |
| Database error | Delete `hospital.db` and restart backend |
| Swagger shows 401 | Use `/api/auth/login` first to get token |

---

## **Your System Status**

```
✅ Backend: http://localhost:8000
✅ Frontend: http://localhost:3000
✅ Database: SQLite (hospital.db)
✅ SMS Alerts: Enabled
✅ Privacy Controls: Enabled
✅ Ready to Use!
```

---

**JUST COPY THE FIRST TWO COMMANDS AND YOU'RE DONE!** 🚀

```powershell
# Terminal 1
cd "e:\project\POC 1st\backend"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2
cd "e:\project\POC 1st\frontend"
npm run dev
```
