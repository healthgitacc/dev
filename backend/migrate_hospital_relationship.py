#!/usr/bin/env python3
"""
Database migration script to add hospital_id column to users table.
This script adds the foreign key relationship between users and hospitals.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def migrate_database():
    """Add hospital_id column to users table."""
    print("Running database migration for hospital relationship...\n")
    
    try:
        from app.database import engine
        from sqlalchemy import text
        
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
        from app.database import engine
        from sqlalchemy import text
        
        # Check if hospital_id column exists
        check_sql = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'hospital_id';
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(check_sql)).fetchone()
            if result:
                print(f"✓ hospital_id column exists: {result}")
            else:
                print("❌ hospital_id column not found")
                return False
            
            # Check foreign key constraint
            fk_sql = """
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints 
            WHERE table_name = 'users' AND constraint_type = 'FOREIGN KEY';
            """
            
            fk_result = conn.execute(text(fk_sql)).fetchall()
            if fk_result:
                print(f"✓ Foreign key constraints found: {len(fk_result)}")
                for constraint in fk_result:
                    print(f"  - {constraint[0]}: {constraint[1]}")
            else:
                print("❌ No foreign key constraints found")
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