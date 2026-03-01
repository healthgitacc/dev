#!/usr/bin/env python3
"""
Quick Test: Doctors Search & Appointments (Simplified Version)
Fastest way to test core features
"""

import json
import subprocess
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def curl_request(method, endpoint, data=None, headers=None):
    """Make HTTP request using curl"""
    url = f"{BASE_URL}/api{endpoint}"
    cmd = ["curl", "-s", "-X", method, url, "-H", "Content-Type: application/json"]
    
    if headers:
        for key, value in headers.items():
            cmd.extend(["-H", f"{key}: {value}"])
    
    if data:
        cmd.extend(["-d", json.dumps(data)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout) if result.stdout else {}
    except json.JSONDecodeError:
        return {"error": result.stdout}

print("\n" + "=" * 70)
print("QUICK TEST: DOCTORS & APPOINTMENTS")
print("=" * 70)

# Step 1: Register a patient
print("\n[1] Registering Patient...")
patient_reg = {
    "name": "Quick Test Patient",
    "email": f"quicktest{datetime.now().timestamp()}@hospital.com",
    "password": "QuickTest123!",
    "phone": "9999999999",
    "role": "patient"
}

patient_resp = curl_request("POST", "/auth/register", patient_reg)
patient_token = patient_resp.get("access_token")

if patient_token:
    print("✅ Patient registered")
else:
    print(f"❌ Registration failed: {patient_resp}")
    exit(1)

auth_headers = {"Authorization": f"Bearer {patient_token}"}

# Step 2: List all doctors
print("\n[2] Fetching all doctors...")
doctors_resp = curl_request("GET", "/doctors", headers=auth_headers)

if "items" in doctors_resp:
    doctors = doctors_resp['items']
    print(f"✅ Found {len(doctors)} doctors")
    for doc in doctors[:3]:  # Show first 3
        print(f"   - ID: {doc.get('id')}, Name: {doc.get('user', {}).get('name')}, "
              f"Spec: {doc.get('specialization')}")
    doctor_id = doctors[0]['id'] if doctors else 1
else:
    print(f"❌ Failed to fetch doctors")
    doctor_id = 1

# Step 3: Filter by specialization
print("\n[3] Searching doctors by specialization 'Cardiology'...")
search_resp = curl_request("GET", "/doctors/search/specialization?specialization=Cardiology", 
                          headers=auth_headers)

if "items" in search_resp:
    print(f"✅ Found {len(search_resp['items'])} Cardiology specialist(s)")
    for doc in search_resp['items']:
        print(f"   - {doc.get('user', {}).get('name')} ({doc.get('experience_years')} yrs)")
else:
    print(f"Response: {search_resp}")

# Step 4: Book an appointment
print("\n[4] Booking appointment...")
appt_date = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"

appt_endpoint = (
    f"/appointments?doctor_id={doctor_id}&"
    f"appointment_date={appt_date}&"
    f"duration_minutes=30&"
    f"notes=Quick test appointment"
)

appt_resp = curl_request("POST", appt_endpoint, headers=auth_headers)

if "id" in appt_resp or "appointment_id" in appt_resp:
    print(f"✅ Appointment booked (ID: {appt_resp.get('id')})")
    print(f"   Status: {appt_resp.get('status')}")
else:
    print(f"❌ Failed to book: {appt_resp}")

# Step 5: List patient appointments
print("\n[5] Listing patient appointments...")
list_resp = curl_request("GET", "/appointments", headers=auth_headers)

if "items" in list_resp:
    print(f"✅ Total appointments: {len(list_resp['items'])}")
    for appt in list_resp['items'][:3]:
        print(f"   - Date: {appt.get('appointment_date')}, Status: {appt.get('status')}")
else:
    print(f"Response: {list_resp}")

print("\n" + "=" * 70)
print("✅ QUICK TEST COMPLETE!")
print("=" * 70)
