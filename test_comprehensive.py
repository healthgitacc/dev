#!/usr/bin/env python3
"""
Comprehensive test for Hospital Management System
Tests backend endpoints and frontend pages
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:3001"
API_URL = "http://localhost:8000/api"

def log(msg, status=None):
    icon = "✅" if status == "pass" else "❌" if status == "fail" else "ℹ️"
    print(f"{icon} {msg}")

def test_backend():
    """Test backend API endpoints"""
    log("\n=== BACKEND API TESTS ===")
    
    # Test 1: Register
    log("Testing: User Registration")
    resp = requests.post(f"{API_URL}/auth/register", json={
        "name": "Test User",
        "email": f"test{datetime.now().timestamp()}@test.com",
        "password": "TestPass123!",
        "phone": "+1234567890",
        "role": "patient"
    })
    user_email = json.loads(resp.text).get('email', 'N/A') if resp.status_code == 201 else None
    log(f"  Status: {resp.status_code}", "pass" if resp.status_code == 201 else "fail")
    
    if not user_email:
        # Use existing user
        user_email = "test.pages@hospital.com"
    
    # Test 2: Login
    log("Testing: User Login")
    resp = requests.post(f"{API_URL}/auth/login", json={
        "email": user_email,
        "password": "TestPass123!"
    })
    token = json.loads(resp.text).get('access_token') if resp.status_code == 200 else None
    log(f"  Status: {resp.status_code}", "pass" if resp.status_code == 200 else "fail")
    
    if not token:
        log("  Could not get token, using test flow", "fail")
        return None
    
    # Test 3: Get current user
    log("Testing: Get Current User (/api/auth/me)")
    resp = requests.get(f"{API_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
    log(f"  Status: {resp.status_code}", "pass" if resp.status_code == 200 else "fail")
    
    return token

def test_frontend(token):
    """Test frontend pages"""
    log("\n=== FRONTEND PAGE TESTS ===")
    
    pages = [
        ("/login", "Login Page"),
        ("/register", "Register Page"),
        ("/dashboard", "Dashboard"),
        ("/profile", "Profile"),
        ("/appointments", "Appointments"),
        ("/medical-records", "Medical Records"),
        ("/doctors", "Doctors"),
        ("/patients", "Patients"),
        ("/users", "Users"),
        ("/admin/settings", "Admin Settings"),
        ("/change-password", "Change Password"),
    ]
    
    passed = 0
    failed = 0
    
    for path, name in pages:
        try:
            resp = requests.get(f"{BASE_URL}{path}", timeout=5)
            if resp.status_code == 200:
                # Check if page has actual content (not blank)
                content_length = len(resp.text)
                if content_length > 100:
                    log(f"  {name:20} ({path}) - {resp.status_code} ({content_length} bytes)", "pass")
                    passed += 1
                else:
                    log(f"  {name:20} ({path}) - {resp.status_code} (blank page!)", "fail")
                    failed += 1
            else:
                log(f"  {name:20} ({path}) - Status {resp.status_code}", "fail")
                failed += 1
        except Exception as e:
            log(f"  {name:20} ({path}) - Error: {str(e)[:30]}", "fail")
            failed += 1
    
    log(f"\n  Total: {passed} passed, {failed} failed")
    return passed, failed

def main():
    log("🏥 HOSPITAL MANAGEMENT SYSTEM - COMPREHENSIVE TEST")
    log("=" * 50)
    
    # Test backend
    token = test_backend()
    
    # Test frontend
    passed, failed = test_frontend(token)
    
    # Summary
    log("\n" + "=" * 50)
    if failed == 0 and token:
        log("✅ ALL TESTS PASSED!", "pass")
    else:
        log(f"⚠️  {failed} tests failed - check items above", "fail" if failed > 0 else "pass")
    log("=" * 50)

if __name__ == "__main__":
    main()
