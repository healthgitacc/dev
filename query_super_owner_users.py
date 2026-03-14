#!/usr/bin/env python3
"""
Query Super Owner users from PostgreSQL database.
This script connects to the database and shows available Super Owner credentials.
"""

import os
import sys
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import sessionmaker
import enum


def get_database_url():
    """Get database URL from environment or use default."""
    # Try to get from environment variables
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "hospital_db")
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def query_super_owner_users():
    """Query all Super Owner users from the database."""
    print("Querying Super Owner users from database...\n")
    
    try:
        database_url = get_database_url()
        print(f"Connecting to database: {database_url}")
        engine = create_engine(database_url)
        
        # SQL query to find Super Owner users
        query_sql = """
        SELECT 
            id,
            name,
            email,
            phone,
            role,
            is_active,
            created_at,
            updated_at,
            hospital_id
        FROM users 
        WHERE role = 'super_owner' 
        ORDER BY created_at DESC;
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(query_sql))
            users = result.fetchall()
            
            if users:
                print(f"Found {len(users)} Super Owner user(s):\n")
                print("=" * 80)
                print(f"{'ID':<4} {'Name':<25} {'Email':<30} {'Role':<15} {'Active':<8} {'Hospital ID':<12}")
                print("=" * 80)
                
                for user in users:
                    print(f"{user[0]:<4} {user[1]:<25} {user[2]:<30} {user[4]:<15} {str(user[5]):<8} {str(user[8]):<12}")
                
                print("=" * 80)
                print("\nTo test Super Owner login, use any of these credentials:")
                print("Email: [user email from above]")
                print("Password: [original password used during registration]")
                print("\nNote: You'll need to know the original password for each user.")
                print("If you don't know the password, you can reset it or create a new Super Owner user.")
                
            else:
                print("❌ No Super Owner users found in the database.")
                print("\nTo create a Super Owner user, you can:")
                print("1. Use the registration endpoint with role='super_owner'")
                print("2. Or use the admin interface if available")
                print("3. Or run a database insert query manually")
        
        return len(users) > 0
        
    except Exception as e:
        print(f"❌ Failed to query database: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_super_owner_endpoints():
    """Show available Super Owner endpoints."""
    print("\n" + "=" * 80)
    print("SUPER OWNER ENDPOINTS (Available after login)")
    print("=" * 80)
    print("POST   /api/admin/hospitals/           - Create new hospital")
    print("GET    /api/admin/hospitals/           - List all hospitals")
    print("GET    /api/admin/hospitals/{id}       - Get hospital by ID")
    print("PUT    /api/admin/hospitals/{id}       - Update hospital")
    print("DELETE /api/admin/hospitals/{id}       - Delete hospital")
    print("PATCH  /api/admin/hospitals/{id}/activate - Activate hospital")
    print("PATCH  /api/admin/hospitals/{id}/deactivate - Deactivate hospital")
    print("GET    /api/admin/hospitals/{id}/stats - Get hospital statistics")
    print("=" * 80)
    print("\n🔒 Super Owner ACCESS RESTRICTIONS:")
    print("❌ BLOCKED: /patients/* (all patient data)")
    print("❌ BLOCKED: /doctors/* (all doctor data)")
    print("❌ BLOCKED: /appointments/* (all appointment data)")
    print("❌ BLOCKED: /medical-records/* (all medical records)")
    print("✅ ALLOWED: /admin/hospitals/* (hospital management only)")
    print("=" * 80)


def main():
    """Main function to query Super Owner users."""
    print("Super Owner User Query Tool")
    print("=" * 50)
    
    # Query Super Owner users
    users_found = query_super_owner_users()
    
    # Show available endpoints
    show_super_owner_endpoints()
    
    if users_found:
        print("\n🎉 Super Owner users found! You can now test Super Owner functionality.")
        print("\nTo test Super Owner login:")
        print("1. Use the login endpoint with Super Owner credentials")
        print("2. Get JWT token from response")
        print("3. Use token in Authorization header for hospital management endpoints")
        print("4. Verify that patient/doctor/appointment endpoints are blocked")
    else:
        print("\n⚠️  No Super Owner users found. You'll need to create one first.")
    
    return users_found


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)