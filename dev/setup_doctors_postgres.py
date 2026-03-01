#!/usr/bin/env python3
"""
Setup: Create Dummy Doctors for PostgreSQL with Specialization and Experience
This script creates doctors with specializations for testing appointment booking
"""

import json
import requests
import sys
import time

BASE_URL = "http://localhost:8000"

def api_request(method, endpoint, data=None, headers=None):
    """Make HTTP request"""
    url = f"{BASE_URL}/api{endpoint}"
    try:
        if method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        else:
            return {"error": f"Unknown method: {method}"}
        
        return response.json() if response.text else {}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

print("=" * 80)
print("SETUP: CREATING DUMMY DOCTORS WITH SPECIALIZATIONS")
print("=" * 80)

# Doctor data with specializations and experience
doctors_data = [
    {
        "name": "Dr. Sarah Johnson",
        "email": "dr.sarah@hospital.com",
        "password": "DoctorPass@123",
        "phone": "+1-555-1001",
        "specialization": "Cardiology",
        "experience_years": 12,
        "license_number": "MD-CAR-001"
    },
    {
        "name": "Dr. James Wilson",
        "email": "dr.james@hospital.com",
        "password": "DoctorPass@123",
        "phone": "+1-555-1002",
        "specialization": "Neurology",
        "experience_years": 8,
        "license_number": "MD-NEU-001"
    },
    {
        "name": "Dr. Emily Chen",
        "email": "dr.emily@hospital.com",
        "password": "DoctorPass@123",
        "phone": "+1-555-1003",
        "specialization": "Pediatrics",
        "experience_years": 6,
        "license_number": "MD-PED-001"
    },
    {
        "name": "Dr. Michael Brown",
        "email": "dr.michael@hospital.com",
        "password": "DoctorPass@123",
        "phone": "+1-555-1004",
        "specialization": "Dermatology",
        "experience_years": 10,
        "license_number": "MD-DER-001"
    },
    {
        "name": "Dr. Laura Martinez",
        "email": "dr.laura@hospital.com",
        "password": "DoctorPass@123",
        "phone": "+1-555-1005",
        "specialization": "Orthopedics",
        "experience_years": 15,
        "license_number": "MD-ORT-001"
    },
    {
        "name": "Dr. David Lee",
        "email": "dr.david@hospital.com",
        "password": "DoctorPass@123",
        "phone": "+1-555-1006",
        "specialization": "Oncology",
        "experience_years": 11,
        "license_number": "MD-ONC-001"
    }
]

created_doctors = []

print("\nRegistering doctors...\n")

for i, doctor_data in enumerate(doctors_data, 1):
    print(f"[{i}/{len(doctors_data)}] Creating {doctor_data['name']}...")
    
    # Step 1: Register as doctor
    reg_data = {
        "name": doctor_data["name"],
        "email": doctor_data["email"],
        "password": doctor_data["password"],
        "phone": doctor_data["phone"],
        "role": "doctor"
    }
    
    reg_response = api_request("POST", "/auth/register", reg_data)
    
    # Check for duplicate email
    if "detail" in reg_response and "already registered" in reg_response.get("detail", ""):
        print(f"   ⚠️  Email already registered, skipping...")
        continue
    
    doctor_token = reg_response.get("access_token")
    user_id = reg_response.get("user_id")
    
    if not doctor_token or not user_id:
        print(f"   ❌ Registration failed: {reg_response}")
        continue
    
    print(f"   ✅ Registered (User ID: {user_id})")
    
    # Step 2: Get doctor ID by fetching all doctors
    time.sleep(0.3)
    
    all_doctors = api_request("GET", "/doctors")
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
    
    # Step 3: Update doctor profile with specialization using JSON body
    auth_headers = {"Authorization": f"Bearer {doctor_token}"}
    
    update_data = {
        "specialization": doctor_data["specialization"],
        "experience_years": doctor_data["experience_years"],
        "license_number": doctor_data["license_number"]
    }
    
    update_response = api_request("PUT", f"/doctors/{doctor_id}", update_data, auth_headers)
    
    if "id" in update_response:
        print(f"   ✅ Updated profile:")
        print(f"      Specialization: {update_response.get('specialization')}")
        print(f"      Experience: {update_response.get('experience_years')} years")
        print(f"      License: {update_response.get('license_number')}")
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

print(f"\n✅ Successfully created {len(created_doctors)} doctor(s):\n")
for doc in created_doctors:
    print(f"   ID: {doc['id']:<3} | {doc['name']:<25} | {doc['specialization']:<15} | {doc['email']}")

if created_doctors:
    print("\n📝 Next Steps:")
    print("   1. Log in to http://localhost:3001 with credentials:")
    print("      Email: admin@hospital.com")
    print("      Password: SecurePass@123")
    print("   2. Go to dashboard and search for doctors by specialization")
    print("   3. Test booking appointments with available doctors")
else:
    print("\n⚠️  No doctors were created. Check backend logs for errors.")

print()
