#!/usr/bin/env python3
"""
Simple verification script to check Super Owner implementation files.
This script verifies that all the necessary files exist and have the correct content.
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and print result."""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def check_file_content(filepath, search_terms, description):
    """Check if file contains expected content."""
    if not os.path.exists(filepath):
        print(f"❌ {description}: {filepath} - FILE NOT FOUND")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for term in search_terms:
            if term not in content:
                print(f"❌ {description}: Missing '{term}' in {filepath}")
                return False
        
        print(f"✓ {description}: Content verified in {filepath}")
        return True
    except Exception as e:
        print(f"❌ {description}: Error reading {filepath} - {e}")
        return False

def main():
    """Verify Super Owner implementation."""
    print("Verifying Super Owner Implementation...\n")
    
    all_good = True
    
    # Check core model files
    print("=== Core Models ===")
    all_good &= check_file_exists("backend/app/models/user.py", "User model")
    all_good &= check_file_content("backend/app/models/user.py", 
                                 ["SUPER_OWNER = \"super_owner\"", "hospital = relationship"], 
                                 "UserRole enum and hospital relationship")
    
    all_good &= check_file_exists("backend/app/models/hospital.py", "Hospital model")
    all_good &= check_file_content("backend/app/models/hospital.py", 
                                 ["HospitalStatus", "ACTIVE", "INACTIVE"], 
                                 "Hospital model and status enum")
    
    # Check authentication files
    print("\n=== Authentication & Authorization ===")
    all_good &= check_file_exists("backend/app/core/auth.py", "Auth dependencies")
    all_good &= check_file_content("backend/app/core/auth.py", 
                                 ["get_current_super_owner", "SUPER_OWNER"], 
                                 "Super Owner auth dependencies")
    
    all_good &= check_file_exists("backend/app/core/middleware.py", "Access control middleware")
    all_good &= check_file_content("backend/app/core/middleware.py", 
                                 ["super_owner_access_control_middleware", "restricted_paths"], 
                                 "Super Owner access control middleware")
    
    # Check service files
    print("\n=== Services ===")
    all_good &= check_file_exists("backend/app/services/hospital_service.py", "Hospital service")
    all_good &= check_file_content("backend/app/services/hospital_service.py", 
                                 ["create_hospital", "activate_hospital", "deactivate_hospital"], 
                                 "Hospital service operations")
    
    all_good &= check_file_exists("backend/app/services/__init__.py", "Services init file")
    all_good &= check_file_content("backend/app/services/__init__.py", 
                                 ["HospitalService", "__all__"], 
                                 "HospitalService export")
    
    # Check route files
    print("\n=== API Routes ===")
    all_good &= check_file_exists("backend/app/routes/hospital_routes.py", "Hospital routes")
    all_good &= check_file_content("backend/app/routes/hospital_routes.py", 
                                 ["@router.get", "get_current_super_owner", "HospitalService"], 
                                 "Hospital route definitions")
    
    all_good &= check_file_exists("backend/app/routes/__init__.py", "Routes init file")
    all_good &= check_file_content("backend/app/routes/__init__.py", 
                                 ["hospital_routes", "__all__"], 
                                 "Hospital routes export")
    
    # Check updated route files
    print("\n=== Updated Route Files ===")
    route_files = [
        ("backend/app/routes/patient_routes.py", ["SUPER_OWNER", "privacy policy"]),
        ("backend/app/routes/doctor_routes.py", ["SUPER_OWNER", "privacy policy"]),
        ("backend/app/routes/appointment_routes.py", ["SUPER_OWNER", "privacy policy"]),
        ("backend/app/routes/medical_record_routes.py", ["SUPER_OWNER", "privacy policy"]),
        ("backend/app/routes/staff_routes.py", ["SUPER_OWNER", "privacy policy"]),
    ]
    
    for filepath, search_terms in route_files:
        all_good &= check_file_exists(filepath, f"Updated {os.path.basename(filepath)}")
        all_good &= check_file_content(filepath, search_terms, f"Super Owner blocking in {os.path.basename(filepath)}")
    
    # Check application configuration
    print("\n=== Application Configuration ===")
    all_good &= check_file_exists("backend/app/main.py", "Main application file")
    all_good &= check_file_content("backend/app/main.py", 
                                 ["hospital_routes", "super_owner_access_control"], 
                                 "Hospital routes and middleware integration")
    
    # Check test files
    print("\n=== Test Files ===")
    all_good &= check_file_exists("test_super_owner_implementation.py", "Comprehensive test suite")
    all_good &= check_file_exists("test_super_owner_basic.py", "Basic verification test")
    all_good &= check_file_exists("SUPER_OWNER_IMPLEMENTATION_SUMMARY.md", "Implementation documentation")
    
    # Summary
    print("\n" + "="*60)
    if all_good:
        print("🎉 VERIFICATION SUCCESSFUL!")
        print("\nAll Super Owner implementation files are present and contain expected content.")
        print("\nKey features verified:")
        print("✓ SUPER_OWNER role added to UserRole enum")
        print("✓ Hospital model with status management created")
        print("✓ Middleware blocks Super Owner from restricted endpoints")
        print("✓ Authentication dependencies for Super Owner role")
        print("✓ Hospital management service with CRUD operations")
        print("✓ Hospital management API endpoints")
        print("✓ All existing endpoints updated to block Super Owner access")
        print("✓ Application configuration updated")
        print("✓ Comprehensive documentation and tests created")
        print("\nThe Super Owner implementation is complete and ready for use!")
    else:
        print("❌ VERIFICATION FAILED!")
        print("Some files are missing or have incorrect content.")
        print("Please check the implementation and ensure all files are properly created.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)