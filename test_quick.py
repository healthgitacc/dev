#!/usr/bin/env python
"""Quick test script for API endpoints."""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_register():
    """Test user registration."""
    print("[TEST] Registering user...")
    payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "phone": "+1234567890",
        "role": "patient"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        data = response.json()
        if response.status_code == 201:
            print("[OK] User registered successfully!")
            return data.get("access_token")
        else:
            print(f"[ERROR] Registration failed: {data}")
            return None
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_login(email, password):
    """Test user login."""
    print(f"\n[TEST] Logging in with {email}...")
    payload = {
        "email": email,
        "password": password
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        data = response.json()
        if response.status_code == 200:
            print("[OK] Login successful!")
            return data.get("access_token")
        else:
            print(f"[ERROR] Login failed: {data}")
            return None
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("HOSPITAL MANAGEMENT API TEST")
    print("=" * 60)
    
    # Test registration
    token = test_register()
    
    # Test login
    if token:
        print(f"\nAccess Token: {token[:50]}...")
    
    test_login("testuser@example.com", "TestPassword123!")
    
    print("\n" + "=" * 60)
