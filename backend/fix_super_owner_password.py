#!/usr/bin/env python3
"""
Fix Super Owner password with correct argon2 hash.
This script updates the Super Owner user's password to use the correct hashing method.
"""

import os
import sys
from sqlalchemy import create_engine, text
from passlib.context import CryptContext


def get_database_url():
    """Get database URL from environment or use default."""
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "hospital_db")
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def hash_password_argon2(password: str) -> str:
    """Hash password using argon2 (same as application)."""
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    return pwd_context.hash(password)


def fix_super_owner_password():
    """Fix Super Owner user's password with correct argon2 hash."""
    print("Fixing Super Owner password with correct argon2 hash...\n")
    
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        # Hash the password using argon2 (same as application)
        correct_password_hash = hash_password_argon2("superowner123")
        print(f"Generated argon2 hash for 'superowner123': {correct_password_hash}")
        
        # Update the Super Owner user's password
        update_sql = """
        UPDATE users 
        SET password_hash = :password_hash
        WHERE email = 'super.owner@example.com' AND role = 'super_owner';
        """
        
        with engine.connect() as conn:
            conn.execute(text(update_sql), {"password_hash": correct_password_hash})
            conn.commit()
            print("✓ Updated Super Owner user password with correct argon2 hash")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix Super Owner password: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_password_fix():
    """Verify the password was fixed correctly."""
    print("\nVerifying password fix...\n")
    
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        # Query the Super Owner user
        query_sql = """
        SELECT id, name, email, password_hash, role, is_active
        FROM users 
        WHERE email = 'super.owner@example.com';
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(query_sql)).fetchone()
            if result:
                print("✓ Super Owner user verified after password fix:")
                print(f"  ID: {result[0]}")
                print(f"  Name: {result[1]}")
                print(f"  Email: {result[2]}")
                print(f"  Role: {result[4]}")
                print(f"  Active: {result[5]}")
                print(f"  Password Hash: {result[3][:50]}...")  # Show first 50 chars
                print("\n✅ Password fix successful! Super Owner should now be able to login.")
                return True
            else:
                print("❌ Super Owner user not found after password fix")
                return False
        
    except Exception as e:
        print(f"❌ Failed to verify password fix: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_password_verification():
    """Test that the password can be verified correctly."""
    print("\nTesting password verification...\n")
    
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        
        # Test password verification
        test_password = "superowner123"
        test_hash = hash_password_argon2(test_password)
        is_valid = pwd_context.verify(test_password, test_hash)
        
        print(f"Test password: {test_password}")
        print(f"Generated hash: {test_hash}")
        print(f"Verification result: {is_valid}")
        
        if is_valid:
            print("✅ Password verification test passed!")
            return True
        else:
            print("❌ Password verification test failed!")
            return False
        
    except Exception as e:
        print(f"❌ Password verification test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to fix Super Owner password."""
    print("Super Owner Password Fix Tool")
    print("=" * 50)
    
    # Step 1: Test password verification
    verification_success = test_password_verification()
    
    if verification_success:
        # Step 2: Fix password in database
        fix_success = fix_super_owner_password()
        
        if fix_success:
            # Step 3: Verify fix
            verify_success = verify_password_fix()
            
            if verify_success:
                print("\n🎉 Super Owner password fix complete!")
                print("\nSuper Owner credentials for testing:")
                print("Email: super.owner@example.com")
                print("Password: superowner123")
                print("\nYou can now test Super Owner login functionality.")
                return True
    
    print("\n❌ Super Owner password fix failed. Please check the errors above.")
    return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)