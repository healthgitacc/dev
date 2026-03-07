"""
Script to add more doctors with Indian names and specializations to the database.
This script adds 15 new doctors with diverse specializations and experience years.
"""

import sqlite3
import os
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'backend', 'hospital.db')

def add_more_doctors():
    """Add more doctors with Indian names and specializations"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # New doctors data with Indian names
    new_doctors = [
        # (name, specialization, experience_years, license_number)
        ("Dr. Rajesh Kumar", "Cardiology", 15, "MD-CAR-001"),
        ("Dr. Priya Sharma", "Obstetrics and Gynaecology", 12, "MD-OBG-002"),
        ("Dr. Anil Patel", "Orthopedic Surgery", 14, "MD-ORT-003"),
        ("Dr. Deepti Verma", "Psychiatry", 11, "MD-PSY-004"),
        ("Dr. Vikram Singh", "Neurology", 16, "MD-NEU-005"),
        ("Dr. Ananya Desai", "Dermatology", 10, "MD-DER-006"),
        ("Dr. Suresh Nair", "Gastroenterology", 13, "MD-GAS-007"),
        ("Dr. Neha Gupta", "Radiology", 9, "MD-RAD-008"),
        ("Dr. Arjun Reddy", "Urology", 12, "MD-URO-009"),
        ("Dr. Meera Chopra", "Pediatrics", 11, "MD-PED-010"),
        ("Dr. Karthik Iyer", "Oncology", 14, "MD-ONC-011"),
        ("Dr. Sneha Bhatt", "Pulmonology", 10, "MD-PUL-012"),
        ("Dr. Rohit Saxena", "Nephrology", 13, "MD-NEP-013"),
        ("Dr. Pooja Menon", "Endocrinology", 11, "MD-END-014"),
        ("Dr. Siddhant Roy", "Rheumatology", 12, "MD-RHE-015"),
    ]
    
    try:
        # First, check if doctors table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='doctors'")
        if not cursor.fetchone():
            print("❌ Doctors table does not exist. Please run init_db.py first.")
            return
        
        # Get max user_id to create new users
        cursor.execute("SELECT MAX(id) FROM users")
        max_user_id = cursor.fetchone()[0] or 0
        
        print(f"📊 Current max user_id: {max_user_id}")
        print(f"📋 Adding {len(new_doctors)} new doctors...\n")
        
        added_count = 0
        
        for idx, (name, specialization, experience_years, license_number) in enumerate(new_doctors):
            new_user_id = max_user_id + idx + 1
            
            try:
                # Create user record
                cursor.execute("""
                    INSERT INTO users (name, email, phone, password_hash, role, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    f"doctor.{name.lower().replace(' ', '.').replace('dr.', '')}{new_user_id}@hospital.com",
                    f"+91 9{str(new_user_id).zfill(9)}",
                    "hashed_password_placeholder",
                    "doctor",
                    True,
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat()
                ))
                
                # Create doctor record
                cursor.execute("""
                    INSERT INTO doctors (user_id, specialization, experience_years, license_number, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    new_user_id,
                    specialization,
                    experience_years,
                    license_number,
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat()
                ))
                
                print(f"✅ Added: {name}")
                print(f"   - Specialization: {specialization}")
                print(f"   - Experience: {experience_years} years")
                print(f"   - License: {license_number}")
                print()
                
                added_count += 1
                
            except Exception as e:
                print(f"⚠️  Error adding {name}: {str(e)}")
                continue
        
        # Commit changes
        conn.commit()
        
        # Get final count
        cursor.execute("SELECT COUNT(*) FROM doctors")
        total_doctors = cursor.fetchone()[0]
        
        print(f"\n{'='*60}")
        print(f"✅ SUCCESSFULLY ADDED {added_count} DOCTORS!")
        print(f"{'='*60}")
        print(f"📊 Total doctors in system: {total_doctors}")
        
        # Display final doctor list
        print(f"\n📋 All doctors in system:")
        cursor.execute("""
            SELECT d.id, u.name, d.specialization, d.experience_years, d.license_number
            FROM doctors d
            JOIN users u ON d.user_id = u.id
            ORDER BY d.id
        """)
        
        doctors = cursor.fetchall()
        for doc in doctors:
            print(f"{doc[0]:3} | {doc[1]:25} | {doc[2]:25} | {doc[3]:3} yrs | {doc[4]}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🏥 Hospital Management System - Doctor Addition Script\n")
    add_more_doctors()
