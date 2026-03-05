"""
Debug script to test hospital admin appointment booking
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"

print("=" * 70)
print("HOSPITAL ADMIN APPOINTMENT BOOKING DEBUG")
print("=" * 70)

# Step 1: Register Super Admin
print("\n1️⃣ REGISTERING SUPER ADMIN...")
super_admin_data = {
    "name": "Debug Super Admin",
    "email": f"debug_super_{int(datetime.now().timestamp())}@test.com",
    "password": "SuperAdmin123!",
    "phone": "+1234567890",
    "role": "super_admin"
}
print(f"   Registering: {super_admin_data['email']}")

response = requests.post(f"{BASE_URL}/auth/register", json=super_admin_data)
print(f"   Status: {response.status_code}")
if response.status_code == 201:
    super_admin = response.json()
    super_admin_token = super_admin.get('access_token')
    super_admin_role = super_admin.get('role')
    print(f"   ✓ Token: {super_admin_token[:50]}...")
    print(f"   ✓ Role: {super_admin_role}")
else:
    print(f"   ✗ Error: {response.text}")
    exit(1)

# Step 2: Create Hospital Admin
print("\n2️⃣ CREATING HOSPITAL ADMIN (Super Admin only)...")
hospital_admin_data = {
    "name": "Debug Hospital Admin",
    "email": f"debug_admin_{int(datetime.now().timestamp())}@test.com",
    "password": "HospitalAdmin123!",
    "phone": "+1234567890"
}
print(f"   Creating: {hospital_admin_data['email']}")

headers = {"Authorization": f"Bearer {super_admin_token}"}
response = requests.post(
    f"{BASE_URL}/admin/create-hospital-admin",
    json=hospital_admin_data,
    headers=headers
)
print(f"   Status: {response.status_code}")
if response.status_code == 201:
    hospital_admin = response.json()
    hospital_admin_token = hospital_admin.get('access_token')
    hospital_admin_role = hospital_admin.get('role')
    hospital_admin_id = hospital_admin.get('user_id')
    print(f"   ✓ Token: {hospital_admin_token[:50]}...")
    print(f"   ✓ Role: {hospital_admin_role}")
    print(f"   ✓ User ID: {hospital_admin_id}")
else:
    print(f"   ✗ Error: {response.text}")
    exit(1)

# Step 3: Create Doctor
print("\n3️⃣ CREATING DOCTOR ACCOUNT...")
doctor_data = {
    "name": "Debug Doctor",
    "email": f"debug_doctor_{int(datetime.now().timestamp())}@test.com",
    "password": "DoctorPass123!",
    "phone": "+1234567890",
    "role": "doctor"
}
print(f"   Registering: {doctor_data['email']}")

response = requests.post(f"{BASE_URL}/auth/register", json=doctor_data)
print(f"   Status: {response.status_code}")
if response.status_code == 201:
    doctor = response.json()
    doctor_id = doctor.get('user_id')
    print(f"   ✓ Doctor ID: {doctor_id}")
else:
    print(f"   ✗ Error: {response.text}")
    exit(1)

# Step 4: List Doctors to get correct doctor ID
print("\n4️⃣ LISTING DOCTORS...")
headers = {"Authorization": f"Bearer {hospital_admin_token}"}
response = requests.get(f"{BASE_URL}/doctors", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    doctors = response.json().get('items', [])
    print(f"   ✓ Found {len(doctors)} doctors")
    if doctors:
        doctor_id = doctors[0]['id']
        print(f"   ✓ Using doctor ID: {doctor_id}")
else:
    print(f"   ✗ Error: {response.text}")

# Step 5: Book Appointment
print("\n5️⃣ BOOKING APPOINTMENT (Hospital Admin)...")
tomorrow = datetime.now() + timedelta(days=1)
appointment_date = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0).isoformat() + "Z"

appointment_data = {
    "patient_name": "Debug Patient",
    "patient_email": f"debug_patient_{int(datetime.now().timestamp())}@test.com",
    "patient_phone": "+1234567890",
    "doctor_id": doctor_id,
    "appointment_date": appointment_date,
    "duration_minutes": 30,
    "chief_complaint": "Chest pain",
    "symptoms": "Sharp pain",
    "notes": "Test appointment"
}
print(f"   Patient: {appointment_data['patient_email']}")
print(f"   Doctor ID: {appointment_data['doctor_id']}")
print(f"   Date: {appointment_data['appointment_date']}")
print(f"   Using token: {hospital_admin_token[:50]}...")

headers = {"Authorization": f"Bearer {hospital_admin_token}"}
response = requests.post(
    f"{BASE_URL}/admin/appointments/manual",
    json=appointment_data,
    headers=headers
)
print(f"   Status: {response.status_code}")
if response.status_code == 201:
    appointment = response.json()
    print(f"   ✓ Appointment created ID: {appointment.get('id')}")
    print(f"   ✓ Appointment date: {appointment.get('appointment_date')}")
else:
    print(f"   ✗ Error: {response.text}")
    print(f"   ✗ Response: {response.json()}")
    
print("\n" + "=" * 70)
