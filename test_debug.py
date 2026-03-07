#!/usr/bin/env python
"""Direct test of patient registration endpoint - no test harness overhead"""

import requests
import time

timestamp = int(time.time() * 1000)  # Use milliseconds for more uniqueness

# Register super admin
print(f"Registering super admin...")
response1 = requests.post(
    'http://localhost:8000/api/auth/register',
    json={
        'name': 'Test Super',
        'email': f'super{timestamp}@test.com',
        'password': 'Pass@123456',
        'role': 'super_admin'
    }
)
print(f"Super admin registration: {response1.status_code}")

# Login as super admin
print(f"Logging in...")
response2 = requests.post(
    'http://localhost:8000/api/auth/login',
    json={
        'email': f'super{timestamp}@test.com',
        'password': 'Pass@123456'
    }
)
print(f"Login: {response2.status_code}")
token = response2.json()['access_token']

# Test patient registration
print(f"Registering patient...")
response3 = requests.post(
    'http://localhost:8000/api/admin/patients',
    json={
        'name': 'Test Patient',
        'email': f'patient{timestamp}@test.com',
        'phone': '+1-555-0001',
        'blood_group': 'O+',
        'gender': 'male',
        'medical_history': 'None'
    },
    headers={'Authorization': f'Bearer {token}'}
)
print(f"Patient registration status: {response3.status_code}")
print(f"Response: {response3.json()}")
