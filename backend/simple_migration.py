#!/usr/bin/env python3
"""
Simple database migration script to add hospital_id column to users table.
This script avoids circular imports by using direct SQLAlchemy.
"""

import os
import sys
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, ForeignKey, inspect


def get_database_url():
    """Get database URL from environment or use default."""
    # Try to get from environment variables
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "hospital_db")
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def migrate_database():
    """Add hospital_id column to users table."""
    print("Running database migration for hospital relationship...\n")
    
    try:
        # Create engine directly without importing app modules
        database_url = get_database_url()
        print(f"Connecting to database: {database_url}")
        engine = create_engine(database_url)
        
        # SQL to add hospital_id column
        migration_sql = """
        ALTER TABLE users ADD COLUMN IF NOT EXISTS hospital_id INTEGER;
        ALTER TABLE users ADD CONSTRAINT fk_users_hospital_id 
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL;
        """
        
        print("Executing migration SQL...")
        with engine.connect() as conn:
            conn.execute(text(migration_sql))
            conn.commit()
            print("✓ Migration completed successfully!")
            print("✓ Added hospital_id column to users table")
            print("✓ Added foreign key constraint to hospitals table")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_migration():
    """Verify the migration was successful."""
    print("\nVerifying migration...\n")
    
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        inspector = inspect(engine)
        
        # Check if hospital_id column exists in users table
        columns = inspector.get_columns('users')
        hospital_id_exists = any(col['name'] == 'hospital_id' for col in columns)
        
        if hospital_id_exists:
            print("✓ hospital_id column exists in users table")
        else:
            print("❌ hospital_id column not found in users table")
            return False
        
        # Check foreign key constraints
        foreign_keys = inspector.get_foreign_keys('users')
        hospital_fk_exists = any('hospital_id' in fk['constrained_columns'] for fk in foreign_keys)
        
        if hospital_fk_exists:
            print("✓ Foreign key constraint for hospital_id found")
        else:
            print("❌ No foreign key constraint for hospital_id found")
            return False
        
        print("\n✅ Migration verification successful!")
        return True
        
    except Exception as e:
        print(f"❌ Migration verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the migration and verification."""
    print("Hospital Relationship Migration Tool")
    print("=" * 50)
    
    # Run migration
    migration_success = migrate_database()
    
    if migration_success:
        # Verify migration
        verification_success = verify_migration()
        
        if verification_success:
            print("\n🎉 Migration completed successfully!")
            print("\nNext steps:")
            print("1. Restart your application")
            print("2. Test the database connection")
            print("3. Verify Super Owner functionality")
            return True
        else:
            print("\n❌ Migration verification failed")
            return False
    else:
        print("\n❌ Migration failed")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)