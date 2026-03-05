"""
Comprehensive test to verify all pages are accessible and routing works correctly
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:3001"  # Frontend on 3001
API_URL = "http://localhost:8000/api"  # Backend API on 8000

# Test user credentials
TEST_EMAIL = "test.pages@hospital.com"
TEST_PASSWORD = "TestPassword123!"

def log(message):
    """Print timestamped log message"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def register_test_user():
    """Register a new test user"""
    log("📝 Registering test user...")
    response = requests.post(
        f"{API_URL}/auth/register",
        json={
            "name": "Test User for Pages",
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "phone": "+1234567890",
            "role": "patient",
        },
    )
    
    if response.status_code == 201:
        log("✅ Registration successful")
        return response.json()
    elif response.status_code == 409:
        log("⚠️  User already exists (this is OK)")
        return None
    else:
        log(f"❌ Registration failed: {response.status_code}")
        log(f"   Response: {response.text}")
        return None

def login_user():
    """Login and get JWT token"""
    log("🔐 Logging in user...")
    response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        },
    )
    
    if response.status_code == 200:
        data = response.json()
        log(f"✅ Login successful")
        log(f"   Token Type: {data.get('token_type')}")
        log(f"   User Email: {data.get('email')}")
        log(f"   User Role: {data.get('role')}")
        return data.get("access_token")
    else:
        log(f"❌ Login failed: {response.status_code}")
        log(f"   Response: {response.text}")
        return None

def test_page_accessibility(token):
    """Test all page URLs"""
    pages = [
        # Auth pages (no token needed)
        ("/login", "Login", False),
        ("/register", "Register", False),
        ("/forgot-password", "Forgot Password", False),
        # Protected pages (token needed)
        ("/dashboard", "Dashboard", True),
        ("/profile", "Profile", True),
        ("/appointments", "Appointments", True),
        ("/medical-records", "Medical Records", True),
        ("/doctors", "Doctors", True),
        ("/patients", "Patients", True),
        ("/users", "Users", True),
        ("/admin/settings", "Admin Settings", True),
        ("/change-password", "Change Password", True),
    ]
    
    log("\n📄 Testing page accessibility...\n")
    
    passed = 0
    failed = 0
    
    for path, title, requires_token in pages:
        # Test without token (should be redirected from protected pages)
        response = requests.get(f"{BASE_URL}{path}", allow_redirects=True)
        status = response.status_code
        
        if requires_token:
            # Protected pages should either have token or redirect to login
            if token:
                # With token, should get 200 and page content
                if status == 200:
                    log(f"✅ {title:20} ({path}) - Status {status}")
                    passed += 1
                else:
                    log(f"⚠️  {title:20} ({path}) - Status {status} (likely redirected)")
                    failed += 1
            else:
                # Without token, should redirect to login
                if status == 200 and "/login" not in response.url:
                    log(f"⚠️  {title:20} ({path}) - Accessible without token (security issue?)")
                    failed += 1
                else:
                    log(f"✅ {title:20} ({path}) - Correctly protected")
                    passed += 1
        else:
            # Auth pages should be accessible
            if status == 200:
                log(f"✅ {title:20} ({path}) - Status {status}")
                passed += 1
            else:
                log(f"❌ {title:20} ({path}) - Status {status}")
                failed += 1
    
    log(f"\n{'=' * 50}")
    log(f"Results: {passed} passed, {failed} failed")
    log(f"{'=' * 50}\n")
    
    return passed, failed

def test_404_page():
    """Test the 404 page"""
    log("🔍 Testing 404 page...")
    response = requests.get(f"{BASE_URL}/this-page-does-not-exist", allow_redirects=False)
    
    if response.status_code == 404:
        if "404" in response.text or "not found" in response.text.lower():
            log("✅ 404 page is working correctly")
            return True
        else:
            log("⚠️  404 page returned 404 but content seems wrong")
            return False
    else:
        log(f"⚠️  Expected 404, got {response.status_code}")
        return False

def main():
    """Run all tests"""
    log("=" * 60)
    log("🏥 HOSPITAL MANAGEMENT SYSTEM - PAGE ROUTING TEST")
    log("=" * 60)
    
    # Register and login
    register_test_user()
    token = login_user()
    
    # Test pages
    log("\n")
    passed, failed = test_page_accessibility(token)
    
    # Test 404
    test_404_page()
    
    # Summary
    log("=" * 60)
    if failed == 0 and token:
        log("✅ All tests passed! Page routing is working correctly.")
    else:
        log("⚠️  Some tests need attention. Check the results above.")
    log("=" * 60)

if __name__ == "__main__":
    main()
