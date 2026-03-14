#!/usr/bin/env python3
"""
Database connection test to diagnose timeout issues.
This script tests database connectivity and configuration.
"""

import sys
import os
import time
import traceback

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_database_connection():
    """Test database connection and configuration."""
    print("Testing Database Connection...\n")
    
    try:
        # Test 1: Import database components
        print("1. Testing imports...")
        from app.database import engine, SessionLocal, Base
        from app.core.config import settings
        print("   ✓ Database imports successful")
        print(f"   ✓ Database URL: {settings.DATABASE_URL}")
        print(f"   ✓ Use SQLite: {settings.USE_SQLITE}")
        print(f"   ✓ SQL Echo: {settings.SQL_ECHO}")
        
        # Test 2: Test engine creation
        print("\n2. Testing database engine...")
        print(f"   ✓ Engine created successfully")
        print(f"   ✓ Engine URL: {engine.url}")
        print(f"   ✓ Engine pool class: {engine.pool.__class__.__name__}")
        
        # Test 3: Test session creation
        print("\n3. Testing database session...")
        start_time = time.time()
        db = SessionLocal()
        connection_time = time.time() - start_time
        print(f"   ✓ Session created in {connection_time:.2f} seconds")
        
        # Test 4: Test actual database connection
        print("\n4. Testing database connection...")
        from sqlalchemy import text
        start_time = time.time()
        result = db.execute(text("SELECT 1")).scalar()
        connection_time = time.time() - start_time
        print(f"   ✓ Database query successful in {connection_time:.2f} seconds")
        print(f"   ✓ Query result: {result}")
        
        # Test 5: Test table creation
        print("\n5. Testing table creation...")
        start_time = time.time()
        Base.metadata.create_all(bind=engine)
        creation_time = time.time() - start_time
        print(f"   ✓ Tables created in {creation_time:.2f} seconds")
        
        # Test 6: Test user table access
        print("\n6. Testing user table access...")
        from app.models import User
        start_time = time.time()
        user_count = db.query(User).count()
        query_time = time.time() - start_time
        print(f"   ✓ User table query successful in {query_time:.2f} seconds")
        print(f"   ✓ User count: {user_count}")
        
        db.close()
        print("\n🎉 All database tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False


def test_configuration():
    """Test application configuration."""
    print("\nTesting Application Configuration...\n")
    
    try:
        from app.core.config import settings
        
        print("Configuration values:")
        print(f"  API Title: {settings.API_TITLE}")
        print(f"  API Version: {settings.API_VERSION}")
        print(f"  Debug: {settings.DEBUG}")
        print(f"  Server Host: {settings.SERVER_HOST}")
        print(f"  Server Port: {settings.SERVER_PORT}")
        print(f"  Database URL: {settings.DATABASE_URL}")
        print(f"  Use SQLite: {settings.USE_SQLITE}")
        print(f"  SQL Echo: {settings.SQL_ECHO}")
        print(f"  Secret Key Length: {len(settings.SECRET_KEY)} chars")
        print(f"  Allowed Origins: {settings.ALLOWED_ORIGINS}")
        print(f"  Reminder Enabled: {settings.REMINDER_ENABLED}")
        print(f"  Reminder Hour: {settings.REMINDER_HOUR}")
        print(f"  Reminder Minute: {settings.REMINDER_MINUTE}")
        print(f"  Reminder Hours Before: {settings.REMINDER_HOURS_BEFORE}")
        
        print("\n✅ Configuration test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration test failed: {e}")
        traceback.print_exc()
        return False


def diagnose_timeout_issue():
    """Diagnose potential timeout issues."""
    print("\nDiagnosing Timeout Issues...\n")
    
    issues = []
    
    # Check if .env file exists
    env_file = os.path.join("backend", ".env")
    if not os.path.exists(env_file):
        issues.append("❌ No .env file found - using default configuration")
        print("   Note: Using default configuration from .env.example")
    else:
        print("✓ .env file found")
    
    # Check database configuration
    try:
        from app.core.config import settings
        if "sqlite" in settings.DATABASE_URL.lower():
            print("✓ Using SQLite database (local file-based)")
        else:
            print("✓ Using PostgreSQL database")
            # Check if PostgreSQL is accessible
            try:
                import psycopg2
                conn_params = {
                    'host': settings.DB_HOST,
                    'port': settings.DB_PORT,
                    'user': settings.DB_USER,
                    'password': settings.DB_PASSWORD,
                    'dbname': settings.DB_NAME
                }
                conn = psycopg2.connect(**conn_params)
                conn.close()
                print("✓ PostgreSQL connection successful")
            except Exception as e:
                issues.append(f"❌ PostgreSQL connection failed: {e}")
                print(f"   PostgreSQL connection issue: {e}")
    except Exception as e:
        issues.append(f"❌ Database configuration issue: {e}")
        print(f"   Database configuration issue: {e}")
    
    # Check if SECRET_KEY is secure
    try:
        from app.core.config import settings
        if len(settings.SECRET_KEY) < 32 and not settings.DEBUG:
            issues.append("❌ SECRET_KEY too short for production")
            print("   Warning: SECRET_KEY should be at least 32 characters in production")
        else:
            print("✓ SECRET_KEY length appropriate")
    except Exception as e:
        issues.append(f"❌ SECRET_KEY check failed: {e}")
        print(f"   SECRET_KEY check failed: {e}")
    
    if issues:
        print(f"\n⚠️  Found {len(issues)} potential issues:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✅ No obvious timeout issues detected")
    
    return len(issues) == 0


def main():
    """Run all tests."""
    print("Database Connection Diagnostic Tool")
    print("=" * 50)
    
    # Test configuration first
    config_ok = test_configuration()
    
    # Test database connection
    db_ok = test_database_connection()
    
    # Diagnose timeout issues
    timeout_ok = diagnose_timeout_issue()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"  Database: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"  Timeout Issues: {'✅ NONE' if timeout_ok else '⚠️  FOUND'}")
    
    if config_ok and db_ok and timeout_ok:
        print("\n🎉 All tests passed! Database should be working correctly.")
        print("\nIf you're still experiencing timeouts:")
        print("  1. Check if the database server is running")
        print("  2. Verify network connectivity to database server")
        print("  3. Check database server logs for errors")
        print("  4. Ensure sufficient database connection pool size")
    else:
        print("\n❌ Some tests failed. Please review the issues above.")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)