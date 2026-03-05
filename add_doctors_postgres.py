"""
Script to add doctors with Indian names and specializations to PostgreSQL database.
This script creates both user and doctor records in the PostgreSQL database.
"""

import psycopg2
from datetime import datetime

# PostgreSQL connection details
DB_CONFIG = {
    'host': 'localhost',
    'database': 'hospital',
    'user': 'postgres',
    'password': 'postgres',  # Default password in config.py
    'port': 5432
}

def list_databases():
    """List all available databases"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host='localhost',
            database='postgres',
            user='postgres',
            password='postgres',
            port=5432
        )
        cursor = conn.cursor()
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = cursor.fetchall()
        print("📊 Available PostgreSQL databases:")
        for db in databases:
            print(f"   - {db[0]}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error listing databases: {e}")
        
def add_doctors_to_postgres():
    """Add more doctors with Indian names and specializations to PostgreSQL"""
    
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
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🏥 Hospital Management System - PostgreSQL Doctor Addition Script\n")
        print(f"📊 Connecting to PostgreSQL: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}\n")
        
        # Get max user_id to create new users
        cursor.execute("SELECT MAX(id) FROM public.users")
        result = cursor.fetchone()
        max_user_id = result[0] if result[0] else 0
        
        print(f"📊 Current max user_id: {max_user_id}")
        print(f"📋 Adding {len(new_doctors)} new doctors...\n")
        
        added_count = 0
        
        for idx, (name, specialization, experience_years, license_number) in enumerate(new_doctors):
            new_user_id = max_user_id + idx + 1
            email = f"doctor.{name.lower().replace(' ', '.').replace('dr.', '')}{new_user_id}@hospital.com"
            phone = f"+91 9{str(new_user_id).zfill(9)}"
            
            try:
                # Create user record
                cursor.execute("""
                    INSERT INTO public.users (name, email, phone, password_hash, role, is_active, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    name,
                    email,
                    phone,
                    "hashed_password_placeholder",
                    "doctor",
                    True,
                    datetime.utcnow(),
                    datetime.utcnow()
                ))
                
                user_id = cursor.fetchone()[0]
                
                # Create doctor record
                cursor.execute("""
                    INSERT INTO public.doctors (user_id, specialization, experience_years, license_number, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    user_id,
                    specialization,
                    experience_years,
                    license_number,
                    datetime.utcnow(),
                    datetime.utcnow()
                ))
                
                conn.commit()
                
                print(f"✅ Added: {name}")
                print(f"   - Specialization: {specialization}")
                print(f"   - Experience: {experience_years} years")
                print(f"   - License: {license_number}")
                print(f"   - Email: {email}")
                print()
                
                added_count += 1
                
            except Exception as e:
                conn.rollback()
                print(f"⚠️  Error adding {name}: {str(e)}")
                continue
        
        # Get final count
        cursor.execute("SELECT COUNT(*) FROM public.doctors")
        total_doctors = cursor.fetchone()[0]
        
        print(f"\n{'='*70}")
        print(f"✅ SUCCESSFULLY ADDED {added_count} DOCTORS TO POSTGRESQL!")
        print(f"{'='*70}")
        print(f"📊 Total doctors in PostgreSQL: {total_doctors}\n")
        
        # Display final doctor list
        print(f"📋 All doctors in PostgreSQL:\n")
        cursor.execute("""
            SELECT d.id, u.name, d.specialization, d.experience_years, d.license_number
            FROM public.doctors d
            JOIN public.users u ON d.user_id = u.id
            ORDER BY d.id
        """)
        
        doctors = cursor.fetchall()
        print(f"{'ID':<4} | {'Name':<28} | {'Specialization':<30} | {'Exp':<4} | {'License':<15}")
        print("-" * 90)
        for doc in doctors:
            print(f"{doc[0]:<4} | {doc[1]:<28} | {doc[2]:<30} | {doc[3]:<4} | {doc[4]:<15}")
        
        cursor.close()
        conn.close()
        
    except (Exception, psycopg2.Error) as error:
        print(f"❌ Error connecting to PostgreSQL or executing query: {error}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🏥 Hospital Management System - PostgreSQL Doctor Addition Script\n")
    list_databases()
    print()
    add_doctors_to_postgres()
