"""
Migration script to populate doctor names from users table to doctors table.
Run this script after applying the Alembic migration 002_add_name_to_doctors.

Usage:
    python migrate_doctor_names.py

This script:
1. Connects to the PostgreSQL database
2. Copies doctor names from users table to doctors.name column
3. Verifies all doctors now have names
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://hospital_user:hospital_password@localhost:5432/hospital_db"
)


def migrate_doctor_names():
    """Migrate doctor names from users table to doctors table."""
    try:
        # Create engine and session
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        logger.info("Starting doctor names migration...")
        
        # Check if migration is needed
        result = session.execute(text("""
            SELECT COUNT(*) as null_count FROM doctors WHERE name IS NULL
        """)).fetchone()
        
        null_count = result[0] if result else 0
        
        if null_count == 0:
            logger.info("[OK] All doctors already have names. Migration not needed.")
            session.close()
            return True
        
        logger.info(f"Found {null_count} doctors without names. Starting migration...")
        
        # Migrate names from users table
        session.execute(text("""
            UPDATE doctors
            SET name = (
                SELECT users.name 
                FROM users 
                WHERE users.id = doctors.user_id
            )
            WHERE doctors.name IS NULL
        """))
        
        session.commit()
        logger.info(f"[OK] Successfully migrated {null_count} doctor names")
        
        # Verify migration
        result = session.execute(text("""
            SELECT COUNT(*) as null_count FROM doctors WHERE name IS NULL
        """)).fetchone()
        
        remaining_null = result[0] if result else 0
        
        if remaining_null == 0:
            logger.info("[OK] Migration verification successful - all doctors have names")
            session.close()
            return True
        else:
            logger.error(f"[FAILED] Migration incomplete - {remaining_null} doctors still missing names")
            session.close()
            return False
            
    except Exception as e:
        logger.error(f"[ERROR] Error during migration: {str(e)}")
        if session:
            session.rollback()
            session.close()
        return False


if __name__ == "__main__":
    success = migrate_doctor_names()
    sys.exit(0 if success else 1)
