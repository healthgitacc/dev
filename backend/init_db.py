#!/usr/bin/env python
"""Initialize database tables."""
import os
import sys
from sqlalchemy import create_engine

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def init_db():
    """Create all database tables."""
    try:
        # Import settings after path is set
        from app.core.config import settings
        
        # Construct database URL from environment or use defaults
        if settings.USE_SQLITE or "sqlite" in settings.DATABASE_URL.lower():
            DATABASE_URL = "sqlite:///./hospital.db"
            print(f"[INFO] Using SQLite: {DATABASE_URL}")
            engine = create_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False},
            )
        else:
            DATABASE_URL = settings.DATABASE_URL or f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
            print(f"[INFO] Using PostgreSQL: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
            
            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            
            # Test connection
            try:
                with engine.connect() as conn:
                    print("[OK] Database connection successful!")
            except Exception as e:
                print(f"[ERROR] Cannot connect to database: {str(e)}")
                print("[HELP] Make sure PostgreSQL is running and credentials are correct in .env")
                return False
        
        # Import Base and all models so every table is registered
        from app.models.base import Base
        from app.models import (
            User,
            Doctor,
            Patient,
            Appointment,
            MedicalRecord,
            Hospital,
            HospitalUser,
            Department,
        )

        print("[INFO] Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("[OK] Database tables created successfully!")
        
        if "sqlite" in str(DATABASE_URL).lower():
            print(f"[INFO] Database location: {os.path.abspath('hospital.db')}")
        else:
            print(f"[INFO] Database: postgresql://{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)
