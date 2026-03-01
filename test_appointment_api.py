import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

print("="*80)
print("TESTING APPOINTMENT BOOKING API")
print("="*80)

# Step 1: Login to get token
print("\n[Step 1] Logging in as patient...")
login_data = {
    "email": "test@hospital.com",
    "password": "TestPass123!"
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=5)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        user_data = response.json()
        token = user_data.get('access_token')
        print(f"✅ Login successful!")
        print(f"   Token: {token[:50]}...")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Login error: {e}")
    exit(1)

# Step 2: Try booking appointment with proper auth
print("\n[Step 2] Booking appointment with API...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

params = {
    "doctor_id": 1,
    "appointment_date": "2026-03-01T14:00:00",
    "duration_minutes": 30,
    "notes": "Test appointment"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/appointments",
        headers=headers,
        json=params,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code in [200, 201]:
        print("✅ Appointment booked successfully!")
        appointment = response.json()
        print(f"   Appointment ID: {appointment.get('id')}")
        print(f"   Date: {appointment.get('appointment_date')}")
        print(f"   Doctor ID: {appointment.get('doctor_id')}")
    else:
        print(f"❌ Booking failed!")
        try:
            error_data = response.json()
            print(f"   Error: {error_data}")
        except:
            print(f"   Raw response: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request error: {e}")
    print(f"   Make sure backend is running on http://localhost:8000")
except json.JSONDecodeError:
    print(f"❌ Invalid JSON response")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print("\n" + "="*80)
