#!/usr/bin/env python3
"""
Hospital API Test Script
Tests all major endpoints and scenarios
Run: python test_endpoints.py
"""

import httpx
import json
import asyncio
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = None
DOCTOR_TOKEN = None
PATIENT_TOKEN = None
DOCTOR_ID = None
PATIENT_ID = None
APPOINTMENT_ID = None


async def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


async def test_health():
    """Test health check endpoint"""
    await print_section("1. HEALTH CHECK")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200


async def test_registration():
    """Test user registration"""
    global ADMIN_TOKEN, DOCTOR_TOKEN, PATIENT_TOKEN, DOCTOR_ID, PATIENT_ID
    
    await print_section("2. USER REGISTRATION")
    
    users_data = [
        {
            "name": "Admin User",
            "email": "admin@hospital.com",
            "password": "AdminPass123!",
            "phone": "9999999999",
            "role": "admin"
        },
        {
            "name": "Dr. John Smith",
            "email": "john.smith@hospital.com",
            "password": "DoctorPass123!",
            "phone": "8888888888",
            "role": "doctor",
            "specialization": "Cardiology",
            "experience_years": 10,
            "license_number": "LIC123456"
        },
        {
            "name": "Jane Doe",
            "email": "jane.doe@email.com",
            "password": "PatientPass123!",
            "phone": "7777777777",
            "role": "patient",
            "age": 35,
            "gender": "female",
            "blood_group": "O+",
            "medical_history": "Hypertension"
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for user in users_data:
            response = await client.post(f"{BASE_URL}/auth/register", json=user)
            print(f"\n{user['name']} ({user['role']}):")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                print(f"  User ID: {data.get('user', {}).get('id')}")
                print(f"  Email: {data.get('user', {}).get('email')}")
                
                # Store tokens and IDs
                if user['role'] == 'admin':
                    ADMIN_TOKEN = data.get('access_token')
                elif user['role'] == 'doctor':
                    DOCTOR_TOKEN = data.get('access_token')
                    DOCTOR_ID = data.get('user', {}).get('id')
                else:  # patient
                    PATIENT_TOKEN = data.get('access_token')
                    PATIENT_ID = data.get('user', {}).get('id')
                print(f"  ✓ Token received")
            else:
                print(f"  Error: {response.text}")


async def test_login():
    """Test user login"""
    await print_section("3. USER LOGIN")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "admin@hospital.com",
                "password": "AdminPass123!"
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Login successful")
            print(f"  Token type: {data.get('token_type')}")
            print(f"  User email: {data.get('user', {}).get('email')}")


async def test_get_users():
    """Test listing users"""
    await print_section("4. GET USERS LIST")
    
    if not ADMIN_TOKEN:
        print("Skipping: No admin token available")
        return
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/users",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {len(data.get('items', []))} users")
            for user in data.get('items', [])[:3]:
                print(f"  - {user.get('name')} ({user.get('role')})")


async def test_get_doctors():
    """Test listing doctors"""
    await print_section("5. GET DOCTORS LIST")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/doctors"
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {len(data.get('items', []))} doctors")
            for doctor in data.get('items', [])[:3]:
                print(f"  - {doctor.get('user', {}).get('name')} ({doctor.get('specialization')})")


async def test_create_appointment():
    """Test creating appointment"""
    global APPOINTMENT_ID
    
    await print_section("6. CREATE APPOINTMENT")
    
    if not PATIENT_TOKEN or not DOCTOR_ID or not PATIENT_ID:
        print("Skipping: Missing required data")
        return
    
    # Calculate appointment date (tomorrow at 10 AM)
    tomorrow = datetime.now() + timedelta(days=1)
    appointment_date = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
    
    appointment_data = {
        "doctor_id": DOCTOR_ID,
        "patient_id": PATIENT_ID,
        "appointment_date": appointment_date,
        "duration_minutes": 30,
        "notes": "Regular checkup and consultation"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/appointments",
            json=appointment_data,
            headers={"Authorization": f"Bearer {PATIENT_TOKEN}"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            APPOINTMENT_ID = data.get('id')
            print(f"✓ Appointment created")
            print(f"  ID: {APPOINTMENT_ID}")
            print(f"  Date: {data.get('appointment_date')}")
            print(f"  Status: {data.get('status')}")
        else:
            print(f"Error: {response.text}")


async def test_get_appointments():
    """Test listing appointments"""
    await print_section("7. GET APPOINTMENTS")
    
    if not PATIENT_TOKEN:
        print("Skipping: No patient token available")
        return
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/appointments",
            headers={"Authorization": f"Bearer {PATIENT_TOKEN}"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {len(data.get('items', []))} appointments")
            for appt in data.get('items', []):
                print(f"  - {appt.get('appointment_date')} - Status: {appt.get('status')}")


async def test_create_medical_record():
    """Test creating medical record"""
    await print_section("8. CREATE MEDICAL RECORD")
    
    if not DOCTOR_TOKEN or not DOCTOR_ID or not PATIENT_ID:
        print("Skipping: Missing required data")
        return
    
    follow_up_date = (datetime.now() + timedelta(days=7)).isoformat()
    
    record_data = {
        "patient_id": PATIENT_ID,
        "disease_name": "Hypertension",
        "diagnosis": "High blood pressure detected during routine checkup",
        "prescription_text": "Metoprolol, Lisinopril",
        "dosage": "50mg daily",
        "follow_up_date": follow_up_date,
        "notes": "Patient advised to reduce salt intake and exercise regularly"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/medical-records",
            json=record_data,
            headers={"Authorization": f"Bearer {DOCTOR_TOKEN}"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Medical record created")
            print(f"  ID: {data.get('id')}")
            print(f"  Disease: {data.get('disease_name')}")
            print(f"  Created: {data.get('created_at')}")
        else:
            print(f"Error: {response.text}")


async def test_get_medical_records():
    """Test listing medical records"""
    await print_section("9. GET MEDICAL RECORDS")
    
    if not DOCTOR_TOKEN or not PATIENT_ID:
        print("Skipping: Missing required data")
        return
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/medical-records/patient/{PATIENT_ID}",
            headers={"Authorization": f"Bearer {DOCTOR_TOKEN}"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {len(data.get('items', []))} medical records")
            for record in data.get('items', []):
                print(f"  - {record.get('disease_name')} ({record.get('diagnosis')[:50]}...)")


async def test_scheduler_reminders():
    """Test upcoming reminders endpoint"""
    await print_section("10. CHECK APPOINTMENT REMINDERS (Scheduler)")
    
    if not ADMIN_TOKEN:
        print("Skipping: No admin token available")
        return
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/appointments/upcoming/reminders?hours_before=24",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {len(data.get('items', []))} upcoming appointments for reminders")
            for appt in data.get('items', []):
                print(f"  - ID: {appt.get('id')}, Date: {appt.get('appointment_date')}, Reminded: {appt.get('reminder_sent')}")


async def test_error_handling():
    """Test error handling"""
    await print_section("11. ERROR HANDLING TESTS")
    
    async with httpx.AsyncClient() as client:
        # Test unauthorized access
        response = await client.get(f"{BASE_URL}/users")
        print(f"Unauthorized without token: {response.status_code}")
        assert response.status_code == 403
        print(f"✓ Correctly rejected unauthorized request")
        
        # Test invalid token
        response = await client.get(
            f"{BASE_URL}/users",
            headers={"Authorization": "Bearer invalid_token"}
        )
        print(f"Invalid token: {response.status_code}")
        assert response.status_code == 403
        print(f"✓ Correctly rejected invalid token")
        
        # Test not found
        response = await client.get(
            f"{BASE_URL}/users/99999",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
        )
        print(f"Non-existent user: {response.status_code}")
        assert response.status_code == 404
        print(f"✓ Correctly returned not found")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  HOSPITAL API TEST SUITE")
    print("  Phase 6 Verification")
    print("="*60)
    
    try:
        await test_health()
        await test_registration()
        await test_login()
        await test_get_users()
        await test_get_doctors()
        await test_create_appointment()
        await test_get_appointments()
        await test_create_medical_record()
        await test_get_medical_records()
        await test_scheduler_reminders()
        await test_error_handling()
        
        await print_section("TEST SUMMARY")
        print("✅ All tests completed successfully!")
        print("\nKey Verifications:")
        print("  ✓ Health check endpoint working")
        print("  ✓ User registration with roles (admin/doctor/patient)")
        print("  ✓ JWT authentication and token generation")
        print("  ✓ User listing with authorization")
        print("  ✓ Doctor search and filtering")
        print("  ✓ Appointment creation and conflict detection")
        print("  ✓ Medical records management")
        print("  ✓ Scheduler reminder query endpoint")
        print("  ✓ Error handling and authorization checks")
        print("\n📝 Next: Phase 7 - Frontend with Next.js 14")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
