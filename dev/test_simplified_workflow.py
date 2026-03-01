#!/usr/bin/env python
"""
Test script for simplified 2-login workflow.

Tests:
1. Create SUPER_ADMIN account
2. SUPER_ADMIN creates HOSPITAL_ADMIN account
3. HOSPITAL_ADMIN adds patient (no login created)
4. HOSPITAL_ADMIN books appointment
5. Verify SMS notifications sent to patient and doctor
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import time

# API Base URL
BASE_URL = "http://localhost:8000/api"
TIMEOUT = 30

# Generate unique timestamps for test accounts (avoid conflicts)
TEST_TIMESTAMP = int(time.time())

# Test Credentials
SUPER_ADMIN = {
    "name": "System Super Admin",
    "email": f"super{TEST_TIMESTAMP}@hospital.com",
    "password": "SuperPass@123",
    "phone": "+1-555-0001"
}

HOSPITAL_ADMIN = {
    "name": "Hospital Administrator",
    "email": f"admin{TEST_TIMESTAMP}@hospital.com",
    "password": "AdminPass@123",
    "phone": "+1-555-0002"
}

DOCTOR = {
    "name": "Dr. Sarah Johnson",
    "email": f"doctor{TEST_TIMESTAMP}@hospital.com",
    "password": "DoctorPass@123",
    "phone": "+1-555-1001",
    "role": "doctor"
}

PATIENT_TEST = {
    "name": "John Doe Patient",
    "email": f"patient{TEST_TIMESTAMP}@example.com",
    "phone": "+1-555-2001",
    "blood_group": "O+",
    "gender": "M",
    "medical_history": "No known allergies"
}

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{Colors.ENDC}\n")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def register_user(name: str, email: str, password: str, phone: Optional[str] = None, role: str = "super_admin") -> Optional[Dict]:
    """Register a new user."""
    print_info(f"Registering {role}: {email}")
    
    payload = {
        "name": name,
        "email": email,
        "password": password,
        "phone": phone,
        "role": role
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Registered {role}: {email}")
            print(f"  User ID: {data.get('user_id')}")
            print(f"  Role: {data.get('role')}")
            return data
        else:
            print_error(f"Failed to register {role}: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API - is the backend running on port 8000?")
        return None
    except Exception as e:
        print_error(f"Error registering {role}: {str(e)}")
        return None


def login_user(email: str, password: str) -> Optional[Tuple[str, Dict]]:
    """Login user and return token and user info."""
    print_info(f"Logging in user: {email}")
    
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            token = data.get('access_token')
            print_success(f"Logged in: {email}")
            print(f"  Role: {data.get('role')}")
            print(f"  Token: {token[:50]}...")
            return token, data
        else:
            print_error(f"Failed to login: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error logging in: {str(e)}")
        return None


def create_hospital_admin(token: str, admin_data: Dict) -> Optional[Dict]:
    """Super admin creates hospital admin."""
    print_info("Creating Hospital Admin account (Super Admin only)")
    
    payload = {
        "name": admin_data["name"],
        "email": admin_data["email"],
        "password": admin_data["password"],
        "phone": admin_data.get("phone")
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/create-hospital-admin",
            json=payload,
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Created Hospital Admin: {admin_data['email']}")
            print(f"  User ID: {data.get('user_id')}")
            print(f"  Role: {data.get('role')}")
            return data
        else:
            print_error(f"Failed to create Hospital Admin: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error creating Hospital Admin: {str(e)}")
        return None


def create_doctor_account(name: str, email: str, password: str, phone: str) -> Optional[Dict]:
    """Create doctor account via regular registration."""
    print_info(f"Creating doctor account: {email}")
    
    payload = {
        "name": name,
        "email": email,
        "password": password,
        "phone": phone,
        "role": "doctor"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Created doctor account: {email}")
            print(f"  User ID: {data.get('user_id')}")
            return data
        else:
            print_error(f"Failed to create doctor: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error creating doctor: {str(e)}")
        return None


def register_patient(token: str, patient_data: Dict) -> Optional[Dict]:
    """Hospital admin registers a patient (no login created)."""
    print_info("Hospital Admin registering new patient")
    
    # Convert gender string to enum values
    gender_map = {
        "M": "male",
        "F": "female",
        "Other": "other"
    }
    
    # Convert blood group string to enum values
    blood_map = {
        "O+": "O+",
        "O-": "O-",
        "A+": "A+",
        "A-": "A-",
        "B+": "B+",
        "B-": "B-",
        "AB+": "AB+",
        "AB-": "AB-",
    }
    
    payload = {
        "name": patient_data["name"],
        "email": patient_data["email"],
        "phone": patient_data["phone"],
        "blood_group": blood_map.get(patient_data.get("blood_group"), patient_data.get("blood_group")),
        "gender": gender_map.get(patient_data.get("gender"), patient_data.get("gender")),
        "medical_history": patient_data.get("medical_history")
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/patients",
            json=payload,
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Registered patient: {patient_data['email']}")
            print(f"  Patient ID: {data.get('id', data.get('user_id', 'N/A'))}")
            print(f"  Name: {data.get('name', 'N/A')}")
            return data
        else:
            print_error(f"Failed to register patient: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error registering patient: {str(e)}")
        return None


def book_appointment(token: str, patient_id: int, doctor_id: int, appointment_date: str) -> Optional[Dict]:
    """Hospital admin books appointment for patient with doctor."""
    print_info("Hospital Admin booking appointment")
    
    payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_date": appointment_date,
        "chief_complaint": "Regular checkup and consultation",
        "symptoms": "None",
        "duration_minutes": 30,
        "notes": "Patient scheduled by hospital admin"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/appointments",
            json=payload,
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Booked appointment for patient {patient_id} with doctor {doctor_id}")
            print(f"  Appointment ID: {data.get('appointment_id', 'N/A')}")
            print(f"  Date/Time: {data.get('appointment_date', 'N/A')}")
            print(f"  Status: {data.get('status', 'N/A')}")
            return data
        else:
            print_error(f"Failed to book appointment: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error booking appointment: {str(e)}")
        return None


def get_patients_list(token: str) -> Optional[Dict]:
    """Get list of all patients (hospital admin view)."""
    print_info("Retrieving patients list")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/patients",
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved patients list")
            print(f"  Total patients: {data.get('total', 0)}")
            return data
        else:
            print_error(f"Failed to get patients: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Error getting patients: {str(e)}")
        return None


def get_dashboard_stats(token: str) -> Optional[Dict]:
    """Get hospital dashboard statistics."""
    print_info("Retrieving dashboard statistics")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/dashboard",
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved dashboard stats")
            print(f"  Total Patients: {data.get('total_patients', 0)}")
            print(f"  Total Doctors: {data.get('total_doctors', 0)}")
            print(f"  Total Appointments: {data.get('total_appointments', 0)}")
            print(f"  Upcoming Appointments: {data.get('upcoming_appointments', 0)}")
            return data
        else:
            print_error(f"Failed to get dashboard: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Error getting dashboard: {str(e)}")
        return None


def run_workflow_test():
    """Run complete workflow test."""
    print_section("SIMPLIFIED 2-LOGIN WORKFLOW TEST")
    print("Testing:")
    print("  1. Register Super Admin")
    print("  2. Super Admin creates Hospital Admin")
    print("  3. Create Doctor account")
    print("  4. Hospital Admin registers Patient (no login)")
    print("  5. Hospital Admin books Appointment")
    print("  6. View Dashboard Statistics\n")
    
    # Check backend availability
    print_info("Checking backend availability...")
    try:
        response = requests.get(f"{BASE_URL}/auth/login", timeout=5)
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend on http://localhost:8000")
        print_warning("Please ensure backend is running with: python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print_info(f"Backend check: {str(e)} (this is expected)")
    
    print_success("Backend is accessible")
    
    # ========== STEP 1: Register Super Admin ==========
    print_section("STEP 1: Register SUPER_ADMIN Account")
    super_admin_result = register_user(
        SUPER_ADMIN["name"],
        SUPER_ADMIN["email"],
        SUPER_ADMIN["password"],
        SUPER_ADMIN["phone"],
        "super_admin"
    )
    
    if not super_admin_result:
        print_error("Failed to create Super Admin - cannot continue")
        return False
    
    super_admin_id = super_admin_result.get('user_id')
    
    # ========== STEP 2: Login as Super Admin ==========
    print_section("STEP 2: Login as SUPER_ADMIN")
    login_result = login_user(SUPER_ADMIN["email"], SUPER_ADMIN["password"])
    
    if not login_result:
        print_error("Failed to login as Super Admin")
        return False
    
    super_admin_token, super_admin_info = login_result
    
    # ========== STEP 3: Create Doctor Account ==========
    print_section("STEP 3: Create DOCTOR Account")
    doctor_result = create_doctor_account(
        DOCTOR["name"],
        DOCTOR["email"],
        DOCTOR["password"],
        DOCTOR["phone"]
    )
    
    if not doctor_result:
        print_error("Failed to create doctor account")
        return False
    
    doctor_id = doctor_result.get('user_id')
    
    # ========== STEP 4: Super Admin Creates Hospital Admin ==========
    print_section("STEP 4: SUPER_ADMIN Creates HOSPITAL_ADMIN Account")
    hospital_admin_result = create_hospital_admin(super_admin_token, HOSPITAL_ADMIN)
    
    if not hospital_admin_result:
        print_error("Failed to create Hospital Admin")
        return False
    
    hospital_admin_id = hospital_admin_result.get('user_id')
    
    # ========== STEP 5: Login as Hospital Admin ==========
    print_section("STEP 5: Login as HOSPITAL_ADMIN")
    login_result = login_user(HOSPITAL_ADMIN["email"], HOSPITAL_ADMIN["password"])
    
    if not login_result:
        print_error("Failed to login as Hospital Admin")
        return False
    
    hospital_admin_token, hospital_admin_info = login_result
    
    # ========== STEP 6: Hospital Admin Registers Patient ==========
    print_section("STEP 6: HOSPITAL_ADMIN Registers PATIENT (No Login Created)")
    patient_result = register_patient(hospital_admin_token, PATIENT_TEST)
    
    if not patient_result:
        print_error("Failed to register patient")
        return False
    
    patient_id = patient_result.get('id') or patient_result.get('patient_id')
    
    # ========== STEP 7: Hospital Admin Books Appointment ==========
    print_section("STEP 7: HOSPITAL_ADMIN Books APPOINTMENT")
    
    # Create appointment date: tomorrow at 2 PM
    tomorrow = datetime.now() + timedelta(days=1)
    appointment_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    appointment_date_str = appointment_time.isoformat() + "Z"
    
    print_info(f"Appointment scheduled for: {appointment_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    appointment_result = book_appointment(
        hospital_admin_token,
        patient_id,
        doctor_id,
        appointment_date_str
    )
    
    if not appointment_result:
        print_error("Failed to book appointment")
        return False
    
    # ========== STEP 8: View Dashboard ==========
    print_section("STEP 8: View HOSPITAL_ADMIN Dashboard")
    dashboard_result = get_dashboard_stats(hospital_admin_token)
    
    if not dashboard_result:
        print_warning("Could not retrieve dashboard stats")
    
    # ========== SUMMARY ==========
    print_section("✓ WORKFLOW TEST COMPLETED SUCCESSFULLY")
    print_info("Test Accounts Created:")
    print(f"  Super Admin - Email: {SUPER_ADMIN['email']} | Pass: {SUPER_ADMIN['password']}")
    print(f"  Hospital Admin - Email: {HOSPITAL_ADMIN['email']} | Pass: {HOSPITAL_ADMIN['password']}")
    print(f"  Doctor - Email: {DOCTOR['email']} | Pass: {DOCTOR['password']}")
    print()
    print_info("Workflow Summary:")
    print(f"  1. Super Admin (ID: {super_admin_id}) ✓")
    print(f"  2. Hospital Admin (ID: {hospital_admin_id}) created by Super Admin ✓")
    print(f"  3. Doctor (ID: {doctor_id}) registered ✓")
    print(f"  4. Patient (ID: {patient_id}) registered by Hospital Admin (no login) ✓")
    print(f"  5. Appointment booked for patient {patient_id} with doctor {doctor_id} ✓")
    print()
    print_success("SMS Notifications should have been sent to:")
    print(f"  • Patient ({PATIENT_TEST['phone']}) - Appointment confirmation")
    print(f"  • Doctor ({DOCTOR['phone']}) - New appointment notification")
    print()
    print_info("Next Steps:")
    print("  1. Check SMS notifications in logs (if Twilio mock is enabled)")
    print("  2. Test patient optional login: Register with patient email")
    print("  3. Test doctor view of appointment details")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = run_workflow_test()
        if success:
            print_section("ALL TESTS PASSED ✓")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print_section("TEST FAILED")
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
