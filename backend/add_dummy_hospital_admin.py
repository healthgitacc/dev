#!/usr/bin/env python3
"""
Script to add a dummy hospital and hospital admin user for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.security import PasswordManager
from app.database import engine
from app.models.hospital import Hospital
from app.models.user import User
from app.models.hospital_user import HospitalUser
from sqlalchemy.orm import Session
from sqlalchemy import text

def add_dummy_hospital_and_admin():
    """Add a dummy hospital and hospital admin user"""
    
    print("🏥 Adding Dummy Hospital and Hospital Admin...")
    print("=" * 60)
    
    # Create database session
    with Session(engine) as session:
        try:
            # Check if hospital already exists
            existing_hospital = session.query(Hospital).filter(
                Hospital.email == 'demo.hospital@example.com'
            ).first()
            
            if existing_hospital:
                print("❌ Dummy hospital already exists!")
                print(f"   Hospital ID: {existing_hospital.id}")
                print(f"   Name: {existing_hospital.name}")
                print(f"   Email: {existing_hospital.email}")
                return
            
            # Create dummy hospital
            print("🏥 Creating dummy hospital...")
            dummy_hospital = Hospital(
                name="Demo General Hospital",
                email="demo.hospital@example.com",
                phone="+1-555-0123",
                address="123 Medical Center Drive, Health City, HC 12345",
                status="active"
            )
            
            session.add(dummy_hospital)
            session.flush()  # Get the ID
            
            print(f"✅ Dummy hospital created successfully!")
            print(f"   Hospital ID: {dummy_hospital.id}")
            print(f"   Name: {dummy_hospital.name}")
            print(f"   Email: {dummy_hospital.email}")
            
            # Check if hospital admin user already exists
            existing_admin = session.query(User).filter(
                User.email == 'hospital.admin@example.com'
            ).first()
            
            if existing_admin:
                print("❌ Dummy hospital admin already exists!")
                print(f"   User ID: {existing_admin.id}")
                print(f"   Name: {existing_admin.name}")
                print(f"   Email: {existing_admin.email}")
                return
            
            # Create hospital admin user
            print("👤 Creating hospital admin user...")
            hospital_admin_password = "hospital123"
            hospital_admin_hash = PasswordManager.hash_password(hospital_admin_password)
            
            hospital_admin = User(
                name="Hospital Admin Demo",
                email="hospital.admin@example.com",
                phone="+1-555-0124",
                role="hospital_admin",
                password_hash=hospital_admin_hash,
                is_active=True,
            )
            session.add(hospital_admin)
            session.flush()
            # Link user to hospital via HospitalUser (hospitals separate from core tables)
            session.add(HospitalUser(hospital_id=dummy_hospital.id, user_id=hospital_admin.id))
            session.flush()

            print(f"✅ Hospital admin user created successfully!")
            print(f"   User ID: {hospital_admin.id}")
            print(f"   Name: {hospital_admin.name}")
            print(f"   Email: {hospital_admin.email}")
            print(f"   Role: {hospital_admin.role}")
            print(f"   Linked to Hospital ID: {dummy_hospital.id}")
            
            # Commit the transaction
            session.commit()
            
            print("\n🎉 Setup Complete!")
            print("=" * 60)
            print("📋 Test Credentials:")
            print(f"   Hospital Admin Email: hospital.admin@example.com")
            print(f"   Hospital Admin Password: {hospital_admin_password}")
            print(f"   Hospital Name: {dummy_hospital.name}")
            print(f"   Hospital Email: {dummy_hospital.email}")
            print("\n📝 Notes:")
            print("   - Hospital admin is linked to the dummy hospital")
            print("   - All medical menu items should be visible to hospital admin")
            print("   - Use these credentials to test hospital admin functionality")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error: {e}")
            print("   Rolling back changes...")
            return False
    
    return True

if __name__ == "__main__":
    success = add_dummy_hospital_and_admin()
    if success:
        print("\n✅ Dummy hospital and admin setup completed successfully!")
    else:
        print("\n❌ Dummy hospital and admin setup failed!")
        sys.exit(1)