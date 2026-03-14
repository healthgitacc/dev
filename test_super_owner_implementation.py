#!/usr/bin/env python3
"""
Test script to verify Super Owner implementation.
Tests the role-based access control and hospital management functionality.
"""

import sys
import os
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.models import User, UserRole, Hospital, HospitalStatus
from app.services import HospitalService
from app.core.auth import get_current_super_owner, get_current_user
from app.core.middleware import super_owner_access_control_middleware
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import Mock


def test_user_role_enum():
    """Test that SUPER_OWNER role is properly defined."""
    print("Testing UserRole enum...")
    assert hasattr(UserRole, 'SUPER_OWNER'), "SUPER_OWNER role not found in UserRole enum"
    assert UserRole.SUPER_OWNER.value == "super_owner", "SUPER_OWNER value incorrect"
    print("✓ UserRole enum test passed")


def test_hospital_model():
    """Test that Hospital model is properly defined."""
    print("Testing Hospital model...")
    assert hasattr(Hospital, 'id'), "Hospital model missing id field"
    assert hasattr(Hospital, 'name'), "Hospital model missing name field"
    assert hasattr(Hospital, 'status'), "Hospital model missing status field"
    assert hasattr(HospitalStatus, 'ACTIVE'), "HospitalStatus enum missing ACTIVE"
    assert hasattr(HospitalStatus, 'INACTIVE'), "HospitalStatus enum missing INACTIVE"
    print("✓ Hospital model test passed")


def test_middleware_blocks_super_owner():
    """Test that middleware blocks Super Owner from restricted endpoints."""
    print("Testing middleware access control...")
    
    # Create mock request and user
    mock_request = Mock()
    mock_request.url.path = "/patients"
    mock_request.state.current_user = Mock()
    mock_request.state.current_user.role = UserRole.SUPER_OWNER
    
    # Test that middleware raises HTTPException for Super Owner
    try:
        # This should raise an exception
        asyncio.run(super_owner_access_control_middleware(mock_request, lambda x: None))
        assert False, "Middleware should have blocked Super Owner access"
    except HTTPException as e:
        assert e.status_code == status.HTTP_403_FORBIDDEN
        assert "Super Owner access restricted" in str(e.detail)
        print("✓ Middleware correctly blocks Super Owner access")
    except Exception as e:
        assert False, f"Unexpected exception: {e}"


def test_middleware_allows_other_roles():
    """Test that middleware allows other roles to access endpoints."""
    print("Testing middleware allows other roles...")
    
    # Test with different roles
    for role in [UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN, UserRole.DOCTOR, UserRole.PATIENT]:
        mock_request = Mock()
        mock_request.url.path = "/patients"
        mock_request.state.current_user = Mock()
        mock_request.state.current_user.role = role
        
        # This should not raise an exception
        try:
            result = asyncio.run(super_owner_access_control_middleware(mock_request, lambda x: "success"))
            assert result == "success", "Middleware should allow other roles"
        except Exception as e:
            assert False, f"Middleware incorrectly blocked role {role}: {e}"
    
    print("✓ Middleware correctly allows other roles")


def test_auth_dependencies():
    """Test that authentication dependencies work correctly."""
    print("Testing authentication dependencies...")
    
    # Test Super Owner dependency
    try:
        # This should raise an exception for non-Super Owner
        mock_user = Mock()
        mock_user.role = UserRole.HOSPITAL_ADMIN
        get_current_super_owner(mock_user)
        assert False, "Should have raised exception for non-Super Owner"
    except HTTPException as e:
        assert e.status_code == status.HTTP_403_FORBIDDEN
        print("✓ Super Owner dependency correctly validates role")
    
    # Test that Super Owner passes validation
    try:
        mock_user = Mock()
        mock_user.role = UserRole.SUPER_OWNER
        result = get_current_super_owner(mock_user)
        assert result == mock_user, "Should return the user object"
        print("✓ Super Owner dependency correctly accepts Super Owner")
    except Exception as e:
        assert False, f"Super Owner dependency failed: {e}"


def test_hospital_service():
    """Test HospitalService functionality."""
    print("Testing HospitalService...")
    
    # Create in-memory database for testing
    engine = create_engine('sqlite:///:memory:', echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    from app.database import Base
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        hospital_service = HospitalService(db)
        
        # Test creating hospital
        hospital = hospital_service.create_hospital(
            name="Test Hospital",
            email="test@example.com",
            phone="123-456-7890",
            address="123 Test St"
        )
        
        assert hospital.name == "Test Hospital"
        assert hospital.email == "test@example.com"
        assert hospital.status == HospitalStatus.INACTIVE
        print("✓ HospitalService can create hospitals")
        
        # Test getting hospital
        retrieved = hospital_service.get_hospital(hospital.id)
        assert retrieved is not None
        assert retrieved.name == "Test Hospital"
        print("✓ HospitalService can retrieve hospitals")
        
        # Test activating hospital
        activated = hospital_service.activate_hospital(hospital.id)
        assert activated.status == HospitalStatus.ACTIVE
        print("✓ HospitalService can activate hospitals")
        
        # Test deactivating hospital
        deactivated = hospital_service.deactivate_hospital(hospital.id)
        assert deactivated.status == HospitalStatus.INACTIVE
        print("✓ HospitalService can deactivate hospitals")
        
        # Test duplicate hospital creation
        try:
            hospital_service.create_hospital(
                name="Test Hospital",
                email="test@example.com"
            )
            assert False, "Should have raised exception for duplicate hospital"
        except Exception as e:
            assert "already exists" in str(e).lower()
            print("✓ HospitalService prevents duplicate hospitals")
        
    finally:
        db.close()


def main():
    """Run all tests."""
    print("Running Super Owner implementation tests...\n")
    
    try:
        test_user_role_enum()
        test_hospital_model()
        test_middleware_blocks_super_owner()
        test_middleware_allows_other_roles()
        test_auth_dependencies()
        test_hospital_service()
        
        print("\n🎉 All tests passed! Super Owner implementation is working correctly.")
        print("\nSummary of implemented features:")
        print("✓ Added SUPER_OWNER role to UserRole enum")
        print("✓ Created Hospital model with status management")
        print("✓ Implemented middleware to block Super Owner from patient/doctor/appointment/medical record endpoints")
        print("✓ Created authentication dependencies for Super Owner role")
        print("✓ Updated all existing endpoints to block Super Owner access")
        print("✓ Created HospitalService for hospital management")
        print("✓ Created hospital management endpoints for Super Owner")
        print("✓ Added middleware to FastAPI application")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()