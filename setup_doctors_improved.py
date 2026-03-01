#!/usr/bin/env python3
"""
Setup: Create and Configure Doctors with Specializations (Improved Version)
"""

import json
import subprocess
import time

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
print("SETUP: CONFIGURE DOCTORS WITH SPECIALIZATIONS")
print("=" * 80)

# Doctor data
doctors_config = [
    {
        "name": "Dr. Sarah Johnson",
        "email": "dr.sarah.johnson@hospital.com",
        "specialization": "Cardiology",
        "experience_years": 12,
        "license_number": "MD-CAR-001"
    },
    {
        "name": "Dr. James Wilson",
        "email": "dr.james.wilson@hospital.com",
        "specialization": "Neurology",
        "experience_years": 8,
        "license_number": "MD-NEU-001"
    },
    {
        "name": "Dr. Emily Chen",
        "email": "dr.emily.chen@hospital.com",
        "specialization": "Pediatrics",
        "experience_years": 6,
        "license_number": "MD-PED-001"
    },
    {
        "name": "Dr. Michael Brown",
        "email": "dr.michael.brown@hospital.com",
        "specialization": "Dermatology",
        "experience_years": 10,
        "license_number": "MD-DER-001"
    },
    {
        "name": "Dr. Laura Martinez",
        "email": "dr.laura.martinez@hospital.com",
        "specialization": "Cardiology",
        "experience_years": 15,
        "license_number": "MD-CAR-002"
    },
]

# Get list of all existing doctors
print("\n[STEP 1] Fetching all existing doctors...")
all_doctors_response = curl_request("GET", "/doctors")

existing_doctors = {}
if "items" in all_doctors_response:
    for doc in all_doctors_response['items']:
        existing_doctors[doc['email']] = doc['id']
    print(f"✅ Found {len(existing_doctors)} doctors in the system")
else:
    print(f"❌ Could not fetch doctors")
    exit(1)

# Update each doctor with specialization and experience
print("\n[STEP 2] Updating doctor profiles with specializations...")

updated_count = 0
for i, doctor_config in enumerate(doctors_config, 1):
    doctor_email = doctor_config['email']
    doctor_id = existing_doctors.get(doctor_email)
    
    if not doctor_id:
        print(f"\n[{i}] {doctor_config['name']}")
        print(f"    ❌ Doctor not found in database")
        continue
    
    print(f"\n[{i}] Updating {doctor_config['name']} (ID: {doctor_id})...")
    
    # Create update URL with query parameters
    update_endpoint = (
        f"/doctors/{doctor_id}?"
        f"specialization={doctor_config['specialization']}&"
        f"experience_years={doctor_config['experience_years']}&"
        f"license_number={doctor_config['license_number']}"
    )
    
    # For this update, we need a doctor or admin token. Let's register/admin approach
    # Try as admin - look for existing admin tokens or create one
    # For simplicity, we'll create an admin user first
    
    if i == 1:  # Just do it for first doctor to get admin token
        print(f"    Creating admin account for profile updates...")
        admin_reg = {
            "name": "Admin Updater",
            "email": f"admin.setup{time.time():.0f}@hospital.com",
            "password": "AdminPass123!",
            "phone": "9999999999",
            "role": "admin"
        }
        admin_resp = curl_request("POST", "/auth/register", admin_reg)
        admin_token = admin_resp.get("access_token")
        if admin_token:
            print(f"    ✅ Admin account created")
        else:
            print(f"    ❌ Could not create admin account")
            admin_token = None
    
    if admin_token:
        auth_headers = {"Authorization": f"Bearer {admin_token}"}
        update_response = curl_request("PUT", update_endpoint, headers=auth_headers)
        
        if "id" in update_response and update_response.get('specialization'):
            print(f"    ✅ Profile updated successfully:")
            print(f"       - Specialization: {update_response.get('specialization')}")
            print(f"       - Experience: {update_response.get('experience_years')} years")
            print(f"       - License: {update_response.get('license_number')}")
            updated_count += 1
        else:
            print(f"    ❌ Update failed: {update_response}")
    else:
        print(f"    ⚠ Skipping profile update (no admin token)")

print("\n" + "=" * 80)
print("SETUP COMPLETE!")
print("=" * 80)

# Verify by listing doctors again
print("\n[STEP 3] Verification - Listing doctors with specializations...")
verify_response = curl_request("GET", "/doctors")

if "items" in verify_response:
    doctors_with_spec = [d for d in verify_response['items'] if d.get('specialization')]
    print(f"\n✅ {len(doctors_with_spec)}/{len(verify_response['items'])} doctors configured:")
    
    for doc in verify_response['items']:
        if doc.get('specialization'):
            print(f"\n   • {doc.get('name')}")
            print(f"     - Specialization: {doc.get('specialization')}")
            print(f"     - Experience: {doc.get('experience_years')} years")
            print(f"     - License: {doc.get('license_number')}")

print("\n" + "=" * 80)
print("📝 READY FOR TESTING!")
print("=" * 80)
print("\nYou can now:")
print("  1. Run quick test: python test_quick_doctors_appointments.py")
print("  2. Visit frontend: http://localhost:3000")
print("  3. View API docs: http://localhost:8000/docs")
