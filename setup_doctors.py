#!/usr/bin/env python3
"""
Setup: Create Sample Doctors with Specializations
This script creates doctors with different specializations for testing
"""

import json
import subprocess
import sys

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

print("=" * 80)
print("SETUP: CREATING DOCTORS WITH SPECIALIZATIONS")
print("=" * 80)

# Doctor data with specializations
doctors_data = [
    {
        "name": "Dr. Sarah Johnson",
        "email": "dr.sarah.johnson@hospital.com",
        "password": "DoctorPass123!",
        "phone": "+919876543201",
        "specialization": "Cardiology",
        "experience_years": 12,
        "license_number": "MD-CAR-001"
    },
    {
        "name": "Dr. James Wilson",
        "email": "dr.james.wilson@hospital.com",
        "password": "DoctorPass123!",
        "phone": "+919876543202",
        "specialization": "Neurology",
        "experience_years": 8,
        "license_number": "MD-NEU-001"
    },
    {
        "name": "Dr. Emily Chen",
        "email": "dr.emily.chen@hospital.com",
        "password": "DoctorPass123!",
        "phone": "+919876543203",
        "specialization": "Pediatrics",
        "experience_years": 6,
        "license_number": "MD-PED-001"
    },
    {
        "name": "Dr. Michael Brown",
        "email": "dr.michael.brown@hospital.com",
        "password": "DoctorPass123!",
        "phone": "+919876543204",
        "specialization": "Dermatology",
        "experience_years": 10,
        "license_number": "MD-DER-001"
    },
    {
        "name": "Dr. Laura Martinez",
        "email": "dr.laura.martinez@hospital.com",
        "password": "DoctorPass123!",
        "phone": "+919876543205",
        "specialization": "Cardiology",
        "experience_years": 15,
        "license_number": "MD-CAR-002"
    },
]

created_doctors = []

for i, doctor_data in enumerate(doctors_data, 1):
    print(f"\n[{i}/{len(doctors_data)}] Creating {doctor_data['name']}...")
    
    # Step 1: Register as doctor
    reg_data = {
        "name": doctor_data["name"],
        "email": doctor_data["email"],
        "password": doctor_data["password"],
        "phone": doctor_data["phone"],
        "role": "doctor"
    }
    
    reg_response = curl_request("POST", "/auth/register", reg_data)
    doctor_token = reg_response.get("access_token")
    user_id = reg_response.get("user_id")
    
    if not doctor_token:
        print(f"   ❌ Registration failed: {reg_response}")
        continue
    
    print(f"   ✅ Registered as doctor (User ID: {user_id})")
    
    # Step 2: Get doctor ID by fetching all doctors
    # Wait a moment for database sync
    import time
    time.sleep(0.5)
    
    all_doctors = curl_request("GET", "/doctors")
    doctor_id = None
    
    if "items" in all_doctors:
        for doc in all_doctors['items']:
            if doc.get('user', {}).get('email') == doctor_data['email']:
                doctor_id = doc.get('id')
                break
    
    if not doctor_id:
        print(f"   ❌ Could not find doctor ID")
        continue
    
    print(f"   ✅ Found doctor ID: {doctor_id}")
    
    # Step 3: Update doctor profile with specialization
    auth_headers = {"Authorization": f"Bearer {doctor_token}"}
    
    update_endpoint = (
        f"/doctors/{doctor_id}?"
        f"specialization={doctor_data['specialization']}&"
        f"experience_years={doctor_data['experience_years']}&"
        f"license_number={doctor_data['license_number']}"
    )
    
    update_response = curl_request("PUT", update_endpoint, headers=auth_headers)
    
    if "id" in update_response:
        print(f"   ✅ Updated profile:")
        print(f"      - Specialization: {update_response.get('specialization')}")
        print(f"      - Experience: {update_response.get('experience_years')} years")
        print(f"      - License: {update_response.get('license_number')}")
        created_doctors.append({
            "id": doctor_id,
            "name": doctor_data["name"],
            "specialization": doctor_data["specialization"],
            "email": doctor_data["email"]
        })
    else:
        print(f"   ❌ Failed to update profile: {update_response}")

print("\n" + "=" * 80)
print("SETUP COMPLETE!")
print("=" * 80)

print(f"\n✅ Successfully created {len(created_doctors)} doctor(s):")
for doc in created_doctors:
    print(f"   - ID: {doc['id']}, {doc['name']} ({doc['specialization']})")

print("\n📝 Next Steps:")
print("   1. Run: python test_quick_doctors_appointments.py")
print("   2. Or visit: http://localhost:3000")
print("   3. Try searching for doctors by specialization")
print("   4. Book appointments with available doctors")
