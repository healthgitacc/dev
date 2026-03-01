#!/usr/bin/env python3
"""
Full workflow test - Register, Login, and verify Dashboard
"""

import json
import subprocess

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def curl_request(method, endpoint, data=None, token=None):
    """Make HTTP request using curl"""
    url = f"{BASE_URL}/api{endpoint}"
    cmd = ["curl", "-s", "-X", method, url, "-H", "Content-Type: application/json"]
    
    if token:
        cmd.extend(["-H", f"Authorization: Bearer {token}"])
    
    if data:
        cmd.extend(["-d", json.dumps(data)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout) if result.stdout else {}
    except json.JSONDecodeError:
        return {"error": result.stdout}

print("= " * 30)
print("FULL WORKFLOW TEST - Login & Dashboard Access")
print("= " * 30)

# Register
print("\n[1] REGISTERING USER")
print("- " * 30)

registration_data = {
    "name": "Frontend Tester",
    "email": "frontend.test@hospital.com",
    "password": "FrontendTest123!",
    "phone": "9876543210",
    "role": "patient"
}

print(f"Email: {registration_data['email']}")
print(f"Password: {registration_data['password']}")

register_response = curl_request("POST", "/auth/register", registration_data)

if "access_token" in register_response:
    print("[OK] Registration successful!")
    register_token = register_response.get('access_token')
else:
    print(f"[SKIP] User exists or error: {register_response.get('detail')}")
    register_token = None

# Login
print("\n[2] LOGGING IN")
print("- " * 30)

login_data = {
    "email": "frontend.test@hospital.com",
    "password": "FrontendTest123!"
}

login_response = curl_request("POST", "/auth/login", login_data)

if "access_token" in login_response:
    print("[OK] Login successful!")
    access_token = login_response.get('access_token')
    print(f"Response contains: {list(login_response.keys())}")
    print(f"Token: {access_token[:20]}...")
    print(f"Full response:")
    print(json.dumps(login_response, indent=2))
else:
    print(f"[ERROR] Login failed: {login_response}")
    access_token = None

if access_token:
    # Test getting user profile
    print("\n[3] TEST AUTHENTICATED REQUEST (Get Profile)")
    print("- " * 30)
    
    profile_response = curl_request("GET", "/auth/me", token=access_token)
    if "id" in profile_response or "email" in profile_response:
        print("[OK] Authenticated request worked!")
        print(f"Profile: {json.dumps(profile_response, indent=2)}")
    else:
        print(f"[ERROR] Authenticated request failed!")
        print(f"Response: {profile_response}")

    # Instructions for manual testing
    print("\n[4] MANUAL FRONTEND TEST")
    print("- " * 30)
    print(f"1. Go to: {FRONTEND_URL}")
    print(f"2. Login with:")
    print(f"   Email: frontend.test@hospital.com")
    print(f"   Password: FrontendTest123!")
    print(f"3. After login, should see Dashboard page")
    print(f"4. Dashboard should show:")
    print(f"   - Statistics cards")
    print(f"   - Upcoming appointments")
    print(f"   - Medical records")
    
    print("\n" + "= " * 30)
    print("TEST COMPLETE")
    print("= " * 30)
else:
    print("\n[ERROR] Cannot proceed without valid token")

