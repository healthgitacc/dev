#!/usr/bin/env python
"""Initialize PostgreSQL database with all tables - Direct approach."""
import os
import sys
from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import declarative_base

def init_postgres():
    """Create all database tables in PostgreSQL using direct connection."""
    try:
        print("[INFO] Initializing PostgreSQL database...")
        
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except:
            pass
        
        # Database configuration
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "postgres")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "hospital_db")
        
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        print(f"[INFO] Database: {db_host}:{db_port}/{db_name}")
        print(f"[INFO] User: {db_user}")
        
        # Create engine
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        # Test connection
        try:
            with engine.connect() as conn:
                print("[✓] Database connection successful!")
        except Exception as e:
            print(f"[✗] Cannot connect to database: {str(e)}")
            print("[HELP] Make sure PostgreSQL is running and .env file is correct")
            return False
        
        # Create models metadata and create all tables
        try:
            print("[INFO] Creating tables...")
            
            # Add path for imports
            sys.path.insert(0, os.path.dirname(__file__))
            
            # Use a fresh Base for metadata
            Base = declarative_base()
            
            # Import model classes to register them with Base
            from app.models.user import User
            from app.models.doctor import Doctor
            from app.models.patient import Patient
            from app.models.appointment import Appointment
            from app.models.medical_record import MedicalRecord
            
            # Create all tables at once
            Base.metadata.create_all(bind=engine)
            
            # Verify tables were created
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            print(f"\n[✓] All tables created successfully!")
            print(f"[INFO] Created tables ({len(tables)} total):")
            for table in sorted(tables):
                if table not in ['pg_stat_statements']:  # Skip system tables
                    cols = inspector.get_columns(table)
                    print(f"  - {table} ({len(cols)} columns)")
            
            return True
            
        except Exception as e:
            print(f"[✗] Failed to create tables: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    except Exception as e:
        print(f"[✗] Initialization error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = init_postgres()
    sys.exit(0 if success else 1)
