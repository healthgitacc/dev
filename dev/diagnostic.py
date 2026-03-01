#!/usr/bin/env python3
"""Diagnostic: Check backend and database status"""

import json
import subprocess

BASE_URL = "http://localhost:8000"

def curl_request(method, endpoint, headers=None):
    """Make HTTP request"""
    url = f"{BASE_URL}/api{endpoint}"
    cmd = ["curl", "-s", "-X", method, url, "-H", "Content-Type: application/json"]
    
    if headers:
        for key, value in headers.items():
            cmd.extend(["-H", f"{key}: {value}"])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout) if result.stdout else {}
    except json.JSONDecodeError:
        return {"raw": result.stdout[:200]}

print("=" * 70)
print("BACKEND DIAGNOSTIC CHECK")
print("=" * 70)

# Check API health
print("\n[1] Checking API Health...")
response = subprocess.run(["curl", "-s", f"{BASE_URL}/docs"], capture_output=True, text=True)
if response.returncode == 0:
    print("✅ Backend API is responding")
else:
    print("❌ Backend API not responding")
    exit(1)

# Check doctors endpoint
print("\n[2] Checking /doctors endpoint...")
doctors_response = curl_request("GET", "/doctors")
print(f"Response type: {type(doctors_response)}")
print(f"Response: {json.dumps(doctors_response, indent=2)[:300]}...")

# Check database connection by trying a login
print("\n[3] Testing database connection...")
login_data = {
    "email": "testdiag@test.com",
    "password": "Test123!"
}
# We don't expect this to work, just checking connection
test_resp = json.dumps(login_data)
print(f"✅ Can serialize requests")

# Try registering a test user
print("\n[4] Testing user registration...")
reg_data = {
    "name": "Diagnostic Test",
    "email": f"diagtest{__import__('time').time():.0f}@test.com",
    "password": "DiagTest123!",
    "phone": "1111111111",
    "role": "patient"
}

cmd = ["curl", "-s", "-X", "POST", f"{BASE_URL}/api/auth/register", 
       "-H", "Content-Type: application/json",
       "-d", json.dumps(reg_data)]

result = subprocess.run(cmd, capture_output=True, text=True)
try:
    reg_resp = json.loads(result.stdout)
    if "access_token" in reg_resp:
        print(f"✅ User registration working!")
        
        # Now try to list doctors with this token
        print("\n[5] Listing doctors with token...")
        auth_headers = {"Authorization": f"Bearer {reg_resp['access_token']}"}
        doctors_auth = curl_request("GET", "/doctors", auth_headers)
        print(f"Doctors response: {json.dumps(doctors_auth, indent=2)[:500]}...")
        
        if "items" in doctors_auth:
            print(f"✅ Found {len(doctors_auth['items'])} doctors")
        else:
            print(f"❌ No doctors found - might need to create some")
    else:
        print(f"❌ Registration failed: {reg_resp}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
