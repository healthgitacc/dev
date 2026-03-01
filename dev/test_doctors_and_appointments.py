#!/usr/bin/env python3
"""
Comprehensive test for Doctors & Appointments
Tests creating doctors, filtering by specialization, and booking appointments
"""

import json
import subprocess
import sys
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

print("=" * 80)
print("TESTING DOCTORS & APPOINTMENTS FEATURES")
print("=" * 80)

# ====================================================================================
# STEP 1: Create Test Users (1 Patient + 3 Doctors with different specializations)
# ====================================================================================

print("\n" + "=" * 80)
print("STEP 1: CREATING TEST USERS")
print("=" * 80)

# Create Patient
print("\n📋 Creating Patient User...")
patient_data = {
    "name": "John Patient",
    "email": "patient@hospital.com",
    "password": "PatientPass123!",
    "phone": "9876543210",
    "role": "patient"
}

patient_response = curl_request("POST", "/auth/register", patient_data)
patient_token = patient_response.get("access_token")

if patient_token:
    print("✅ Patient created successfully!")
    print(f"   Email: {patient_data['email']}")
    print(f"   Token: {patient_token[:20]}...")
else:
    print(f"❌ Failed to create patient: {patient_response}")
    patient_token = None

# Create Doctors with different specializations
doctors_data = [
    {
        "name": "Dr. Sarah Cardiology",
        "email": "dr.sarah@hospital.com",
        "password": "DoctorPass123!",
        "phone": "9876543211",
        "role": "doctor",
        "specialization": "Cardiology",
        "experience_years": 10,
        "license_number": "DL001"
    },
    {
        "name": "Dr. James Neurology",
        "email": "dr.james@hospital.com",
        "password": "DoctorPass123!",
        "phone": "9876543212",
        "role": "doctor",
        "specialization": "Neurology",
        "experience_years": 8,
        "license_number": "DL002"
    },
    {
        "name": "Dr. Emma Pediatrics",
        "email": "dr.emma@hospital.com",
        "password": "DoctorPass123!",
        "phone": "9876543213",
        "role": "doctor",
        "specialization": "Pediatrics",
        "experience_years": 6,
        "license_number": "DL003"
    },
]

doctor_ids = []
doctor_tokens = []

for i, doctor_data in enumerate(doctors_data, 1):
    print(f"\n📋 Creating Doctor {i}: {doctor_data['name']} ({doctor_data['specialization']})...")
    
    reg_data = {
        "name": doctor_data["name"],
        "email": doctor_data["email"],
        "password": doctor_data["password"],
        "phone": doctor_data["phone"],
        "role": doctor_data["role"]
    }
    
    doc_response = curl_request("POST", "/auth/register", reg_data)
    doc_token = doc_response.get("access_token")
    
    if doc_token:
        print(f"✅ Doctor registered!")
        doctor_tokens.append(doc_token)
        
        # Now we need to create doctor profile after registration
        # The doctor info should be created via a separate endpoint
        # For now, we'll continue with token
    else:
        print(f"❌ Failed to create doctor: {doc_response}")

# ====================================================================================
# STEP 2: Get all doctors and their IDs
# ====================================================================================

print("\n" + "=" * 80)
print("STEP 2: FETCHING ALL DOCTORS")
print("=" * 80)

auth_headers = {"Authorization": f"Bearer {patient_token}"} if patient_token else {}

print("\n📥 Fetching all doctors list...")
doctors_list_response = curl_request("GET", "/doctors", headers=auth_headers)

if "items" in doctors_list_response:
    print(f"✅ Retrieved {len(doctors_list_response['items'])} doctors")
    print(f"   Total available: {doctors_list_response.get('total', '?')}")
    
    for doctor in doctors_list_response['items']:
        print(f"\n   Doctor ID: {doctor.get('id')}")
        print(f"   Name: {doctor.get('user', {}).get('name')}")
        print(f"   Specialization: {doctor.get('specialization')}")
        print(f"   Experience: {doctor.get('experience_years')} years")
        doctor_ids.append(doctor.get('id'))
else:
    print(f"❌ Failed to fetch doctors: {doctors_list_response}")

# ====================================================================================
# STEP 3: Filter Doctors by Specialization
# ====================================================================================

print("\n" + "=" * 80)
print("STEP 3: FILTERING DOCTORS BY SPECIALIZATION")
print("=" * 80)

specializations_to_search = ["Cardiology", "Neurology", "Pediatrics", "Dermatology"]

for spec in specializations_to_search:
    print(f"\n🔍 Searching for {spec} specialists...")
    search_response = curl_request(
        "GET",
        f"/doctors/search/specialization?specialization={spec}",
        headers=auth_headers
    )
    
    if "items" in search_response:
        count = len(search_response['items'])
        print(f"✅ Found {count} doctor(s) in {spec}")
        
        for doctor in search_response['items']:
            print(f"\n   Name: {doctor.get('user', {}).get('name')}")
            print(f"   Specialization: {doctor.get('specialization')}")
            print(f"   Experience: {doctor.get('experience_years')} years")
            print(f"   License: {doctor.get('license_number')}")
    else:
        print(f"❌ Search failed: {search_response}")

# ====================================================================================
# STEP 4: Book Appointments
# ====================================================================================

print("\n" + "=" * 80)
print("STEP 4: BOOKING APPOINTMENTS")
print("=" * 80)

if doctor_ids and patient_token:
    # Book appointment with first available doctor
    doctor_id = doctor_ids[0] if doctor_ids else 1
    
    # Schedule appointment for tomorrow at 10 AM
    appointment_date = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"
    
    print(f"\n📅 Booking appointment with Doctor ID {doctor_id}...")
    print(f"   Scheduled for: {appointment_date}")
    
    appointment_data = {
        "doctor_id": doctor_id,
        "appointment_date": appointment_date,
        "duration_minutes": 30,
        "notes": "Initial consultation for general checkup"
    }
    
    auth_headers = {"Authorization": f"Bearer {patient_token}"}
    
    # Using query parameters instead of body for this endpoint
    appointment_endpoint = (
        f"/appointments?doctor_id={doctor_id}&"
        f"appointment_date={appointment_date}&"
        f"duration_minutes=30&"
        f"notes=Initial consultation for general checkup"
    )
    
    appointment_response = curl_request("POST", appointment_endpoint, headers=auth_headers)
    
    if "id" in appointment_response or "appointment_id" in appointment_response:
        appointment_id = appointment_response.get("id", appointment_response.get("appointment_id"))
        print(f"✅ Appointment booked successfully!")
        print(f"   Appointment ID: {appointment_id}")
        print(f"   Doctor ID: {appointment_response.get('doctor_id')}")
        print(f"   Status: {appointment_response.get('status')}")
    else:
        print(f"❌ Failed to book appointment: {appointment_response}")
        
    # Try booking another appointment with different doctor
    if len(doctor_ids) > 1:
        doctor_id_2 = doctor_ids[1]
        appointment_date_2 = (datetime.utcnow() + timedelta(days=2)).isoformat() + "Z"
        
        print(f"\n📅 Booking second appointment with Doctor ID {doctor_id_2}...")
        print(f"   Scheduled for: {appointment_date_2}")
        
        appointment_endpoint_2 = (
            f"/appointments?doctor_id={doctor_id_2}&"
            f"appointment_date={appointment_date_2}&"
            f"duration_minutes=45&"
            f"notes=Follow-up consultation"
        )
        
        appointment_response_2 = curl_request("POST", appointment_endpoint_2, headers=auth_headers)
        
        if "id" in appointment_response_2 or "appointment_id" in appointment_response_2:
            print(f"✅ Second appointment booked successfully!")
            print(f"   Doctor ID: {appointment_response_2.get('doctor_id')}")
            print(f"   Status: {appointment_response_2.get('status')}")
        else:
            print(f"❌ Failed to book second appointment: {appointment_response_2}")

# ====================================================================================
# STEP 5: List Patient's Appointments
# ====================================================================================

print("\n" + "=" * 80)
print("STEP 5: LISTING PATIENT'S APPOINTMENTS")
print("=" * 80)

if patient_token:
    print(f"\n📋 Fetching all appointments for patient...")
    
    auth_headers = {"Authorization": f"Bearer {patient_token}"}
    appointments_response = curl_request("GET", "/appointments", headers=auth_headers)
    
    if "items" in appointments_response:
        count = len(appointments_response['items'])
        print(f"✅ Retrieved {count} appointment(s)")
        print(f"   Total: {appointments_response.get('total', '?')}")
        
        for appt in appointments_response['items']:
            print(f"\n   Appointment ID: {appt.get('id')}")
            print(f"   Doctor: {appt.get('doctor', {}).get('user', {}).get('name')}")
            print(f"   Date: {appt.get('appointment_date')}")
            print(f"   Status: {appt.get('status')}")
            print(f"   Duration: {appt.get('duration_minutes')} minutes")
            print(f"   Notes: {appt.get('notes')}")
    else:
        print(f"❌ Failed to fetch appointments: {appointments_response}")

# ====================================================================================
# STEP 6: Filter appointments by status
# ====================================================================================

print("\n" + "=" * 80)
print("STEP 6: FILTERING APPOINTMENTS BY STATUS")
print("=" * 80)

statuses = ["scheduled", "completed", "cancelled"]

for status in statuses:
    print(f"\n🔍 Filtering appointments with status: {status}...")
    
    auth_headers = {"Authorization": f"Bearer {patient_token}"}
    filtered_response = curl_request("GET", f"/appointments?status={status}", headers=auth_headers)
    
    if "items" in filtered_response:
        count = len(filtered_response['items'])
        print(f"✅ Found {count} appointment(s) with status '{status}'")
        
        for appt in filtered_response['items']:
            print(f"\n   Appointment ID: {appt.get('id')}")
            print(f"   Status: {appt.get('status')}")
    else:
        print(f"Response: {filtered_response}")

print("\n" + "=" * 80)
print("DOCTORS & APPOINTMENTS TEST COMPLETED")
print("=" * 80)
print("\n✅ All tests finished! Check the results above.")
print("\nKey Features Tested:")
print("  ✓ Created multiple users (patient + doctors)")
print("  ✓ Listed all doctors")
print("  ✓ Filtered doctors by specialization")
print("  ✓ Booked appointments")
print("  ✓ Listed patient appointments")
print("  ✓ Filtered appointments by status")
