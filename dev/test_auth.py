#!/usr/bin/env python3
"""
Simple authentication test - Email and Password
Tests user registration and login
"""

import json
import subprocess
import sys

BASE_URL = "http://localhost:8000"

def curl_request(method, endpoint, data=None):
    """Make HTTP request using curl"""
    url = f"{BASE_URL}/api{endpoint}"
    cmd = ["curl", "-s", "-X", method, url, "-H", "Content-Type: application/json"]
    
    if data:
        cmd.extend(["-d", json.dumps(data)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout) if result.stdout else {}
    except json.JSONDecodeError:
        return {"error": result.stdout}

print("=" * 60)
print("TESTING EMAIL AND PASSWORD AUTHENTICATION")
print("=" * 60)

# Test 1: Register a new user
print("\n1️⃣  REGISTERING A NEW USER")
print("-" * 60)

registration_data = {
    "name": "Test User",
    "email": "test@hospital.com",
    "password": "TestPass123!",
    "phone": "9876543210",
    "role": "patient"
}

print(f"Registering: {registration_data['email']}")
register_response = curl_request("POST", "/auth/register", registration_data)

# Debug: print raw response if available
if not register_response:
    print("   (empty response)")
    register_response = {}

if "access_token" in register_response:
    print("✅ Registration successful!")
    print(f"   Token type: {register_response.get('token_type')}")
    print(f"   User: {register_response.get('user', {}).get('email')}")
    print(f"   Role: {register_response.get('user', {}).get('role')}")
    access_token = register_response.get('access_token')
else:
    print("❌ Registration failed!")
    print(f"   Response: {register_response}")
    access_token = None

# Test 2: Login with email and password
print("\n2️⃣  LOGGING IN WITH EMAIL AND PASSWORD")
print("-" * 60)

login_data = {
    "email": "test@hospital.com",
    "password": "TestPass123!"
}

print(f"Logging in: {login_data['email']}")
login_response = curl_request("POST", "/auth/login", login_data)

if "access_token" in login_response:
    print("✅ Login successful!")
    print(f"   Token type: {login_response.get('token_type')}")
    print(f"   User: {login_response.get('user', {}).get('email')}")
    print(f"   Role: {login_response.get('user', {}).get('role')}")
    login_token = login_response.get('access_token')
else:
    print("❌ Login failed!")
    print(f"   Response: {login_response}")
    login_token = None

# Test 3: Try wrong password
print("\n3️⃣  TESTING WRONG PASSWORD (Should fail)")
print("-" * 60)

wrong_login_data = {
    "email": "test@hospital.com",
    "password": "WrongPassword123!"
}

print(f"Attempting login with wrong password...")
wrong_login_response = curl_request("POST", "/auth/login", wrong_login_data)

if "detail" in wrong_login_response or "error" in wrong_login_response:
    print("✅ Correctly rejected wrong password!")
    print(f"   Response: {wrong_login_response.get('detail', wrong_login_response.get('error'))}")
else:
    print("❌ Should have rejected wrong password!")
    print(f"   Response: {wrong_login_response}")

# Test 4: Try non-existent email
print("\n4️⃣  TESTING NON-EXISTENT EMAIL (Should fail)")
print("-" * 60)

nonexistent_login_data = {
    "email": "nonexistent@hospital.com",
    "password": "AnyPassword123!"
}

print(f"Attempting login with non-existent email...")
nonexistent_response = curl_request("POST", "/auth/login", nonexistent_login_data)

if "detail" in nonexistent_response or "error" in nonexistent_response:
    print("✅ Correctly rejected non-existent email!")
    print(f"   Response: {nonexistent_response.get('detail', nonexistent_response.get('error'))}")
else:
    print("❌ Should have rejected non-existent email!")
    print(f"   Response: {nonexistent_response}")

# Test 5: Try registering duplicate email
print("\n5️⃣  TESTING DUPLICATE EMAIL (Should fail)")
print("-" * 60)

duplicate_data = {
    "name": "Another User",
    "email": "test@hospital.com",
    "password": "AnotherPass123!",
    "phone": "1111111111",
    "role": "doctor"
}

print(f"Attempting to register duplicate email...")
duplicate_response = curl_request("POST", "/auth/register", duplicate_data)

if "detail" in duplicate_response or "error" in duplicate_response:
    print("✅ Correctly rejected duplicate email!")
    print(f"   Response: {duplicate_response.get('detail', duplicate_response.get('error'))}")
else:
    print("❌ Should have rejected duplicate email!")
    print(f"   Response: {duplicate_response}")

print("\n" + "=" * 60)
print("EMAIL AND PASSWORD TEST COMPLETED")
print("=" * 60)
