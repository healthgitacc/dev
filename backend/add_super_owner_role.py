#!/usr/bin/env python3
"""
Add SUPER_OWNER role to the database enum and create a Super Owner user.
This script updates the database to support Super Owner functionality.
"""

import os
import sys
from sqlalchemy import create_engine, text


def get_database_url():
    """Get database URL from environment or use default."""
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "hospital_db")
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def add_super_owner_to_enum():
    """Add SUPER_OWNER to the userrole enum."""
    print("Adding SUPER_OWNER to userrole enum...\n")
    
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        # SQL to add SUPER_OWNER to the enum
        add_enum_sql = """
        ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'super_owner';
        """
        
        with engine.connect() as conn:
            conn.execute(text(add_enum_sql))
            conn.commit()
            print("✓ Added SUPER_OWNER to userrole enum")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to add SUPER_OWNER to enum: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_super_owner_user():
    """Create a Super Owner user for testing."""
    print("\nCreating Super Owner user for testing...\n")
    
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        # Check if Super Owner user already exists
        check_sql = "SELECT COUNT(*) FROM users WHERE email = 'super.owner@example.com';"
        
        with engine.connect() as conn:
            result = conn.execute(text(check_sql)).scalar()
            if result > 0:
                print("⚠️  Super Owner user already exists")
                return True
            
            # Create Super Owner user
            # Password: "superowner123" (hashed using the same method as the application)
            create_sql = """
            INSERT INTO users (name, email, phone, password_hash, role, is_active, created_at, updated_at)
            VALUES (
                'Super Owner Admin',
                'super.owner@example.com',
                '+1234567890',
                '$2b$12$KIXyq8VQZQZQZQZQZQZQZuVQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZ',  -- superowner123
                'super_owner',
                true,
                NOW(),
                NOW()
            );
            """
            
            conn.execute(text(create_sql))
            conn.commit()
            print("✓ Created Super Owner user:")
            print("  Email: super.owner@example.com")
            print("  Password: superowner123")
            print("  Role: super_owner")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create Super Owner user: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_super_owner_user():
    """Verify the Super Owner user was created successfully."""
    print("\nVerifying Super Owner user...\n")
    
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        # Query the Super Owner user
        query_sql = """
        SELECT id, name, email, role, is_active, created_at
        FROM users 
        WHERE email = 'super.owner@example.com';
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(query_sql)).fetchone()
            if result:
                print("✓ Super Owner user verified:")
                print(f"  ID: {result[0]}")
                print(f"  Name: {result[1]}")
                print(f"  Email: {result[2]}")
                print(f"  Role: {result[3]}")
                print(f"  Active: {result[4]}")
                print(f"  Created: {result[5]}")
                return True
            else:
                print("❌ Super Owner user not found")
                return False
        
    except Exception as e:
        print(f"❌ Failed to verify Super Owner user: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_testing_instructions():
    """Show instructions for testing Super Owner functionality."""
    print("\n" + "=" * 80)
    print("SUPER OWNER TESTING INSTRUCTIONS")
    print("=" * 80)
    print("\n1. LOGIN AS SUPER OWNER:")
    print("   POST /api/auth/login")
    print("   Body: {")
    print('     "email": "super.owner@example.com",')
    print('     "password": "superowner123"')
    print("   }")
    print("\n2. GET JWT TOKEN from response")
    print("\n3. TEST HOSPITAL MANAGEMENT ENDPOINTS:")
    print("   Use the JWT token in Authorization header: Bearer <token>")
    print("   - GET /api/admin/hospitals/ (should work)")
    print("   - POST /api/admin/hospitals/ (should work)")
    print("\n4. TEST ACCESS RESTRICTIONS:")
    print("   - GET /api/patients/ (should be BLOCKED - 403 Forbidden)")
    print("   - GET /api/doctors/ (should be BLOCKED - 403 Forbidden)")
    print("   - GET /api/appointments/ (should be BLOCKED - 403 Forbidden)")
    print("   - GET /api/medical-records/ (should be BLOCKED - 403 Forbidden)")
    print("=" * 80)


def main():
    """Main function to set up Super Owner functionality."""
    print("Super Owner Setup Tool")
    print("=" * 50)
    
    # Step 1: Add SUPER_OWNER to enum
    enum_success = add_super_owner_to_enum()
    
    if enum_success:
        # Step 2: Create Super Owner user
        user_success = create_super_owner_user()
        
        if user_success:
            # Step 3: Verify user
            verify_success = verify_super_owner_user()
            
            if verify_success:
                # Step 4: Show instructions
                show_testing_instructions()
                print("\n🎉 Super Owner setup complete! You can now test Super Owner functionality.")
                return True
    
    print("\n❌ Super Owner setup failed. Please check the errors above.")
    return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)