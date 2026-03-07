#!/usr/bin/env python3
"""
Test registration and check SQLite database
"""

import requests
import sqlite3
import json
import time
from datetime import datetime

print("=" * 80)
print("REGISTRATION & DATABASE TEST")
print("=" * 80)

# ============================================================================
# TEST 1: TEST REGISTRATION API
# ============================================================================
print("\n[TEST 1] Testing Registration API...")
print("-" * 80)

timestamp = int(time.time())
register_data = {
    "name": f"Test Patient {timestamp}",
    "email": f"testpat{timestamp}@hospital.com",
    "password": "TestPass123!",
    "phone": "5551234567",
    "role": "patient"
}

try:
    response = requests.post(
        "http://localhost:8000/api/auth/register",
        json=register_data,
        timeout=10
    )
    
    if response.status_code == 201:
        data = response.json()
        if "access_token" in data:
            print(f"✅ Registration API Working!")
            print(f"   - User ID: {data.get('user_id')}")
            print(f"   - Email: {data.get('email')}")
            print(f"   - Role: {data.get('role')}")
            print(f"   - Token received: Yes")
            user_id = data.get('user_id')
        else:
            print(f"❌ API response missing token: {data}")
            user_id = None
    else:
        print(f"❌ API returned status {response.status_code}")
        print(f"   Response: {response.text}")
        user_id = None
except Exception as e:
    print(f"❌ Registration API Error: {str(e)}")
    user_id = None

# ============================================================================
# TEST 2: CHECK SQLITE DATABASE
# ============================================================================
print("\n[TEST 2] Checking SQLite Database...")
print("-" * 80)

try:
    # Connect to SQLite database
    db_path = "e:\\project\\POC 1st\\backend\\hospital.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"✅ SQLite Database connected: {db_path}")
    print(f"   Database size: {__import__('os').path.getsize(db_path) / 1024:.1f} KB")
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    print(f"\n✅ Database Tables ({len(tables)} total):")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"   - {table[0]}: {count} records")
    
    # ========================================================================
    # TEST 3: CHECK USERS TABLE
    # ========================================================================
    print("\n[TEST 3] Checking Users Table...")
    print("-" * 80)
    
    cursor.execute("SELECT id, name, email, role, is_active, created_at FROM users ORDER BY id DESC LIMIT 10")
    users = cursor.fetchall()
    
    print(f"✅ Recent users ({len(users)} shown):")
    print(f"\n   {'ID':<4} {'Name':<30} {'Email':<35} {'Role':<8} {'Active':<7}")
    print(f"   {'-'*4} {'-'*30} {'-'*35} {'-'*8} {'-'*7}")
    
    for user in users:
        user_id_val = user[0]
        name = user[1][:30]
        email = user[2][:35]
        role = user[3][:8]
        active = "Yes" if user[4] else "No"
        print(f"   {user_id_val:<4} {name:<30} {email:<35} {role:<8} {active:<7}")
    
    # ========================================================================
    # TEST 4: CHECK DOCTORS TABLE
    # ========================================================================
    print("\n[TEST 4] Checking Doctors Table...")
    print("-" * 80)
    
    cursor.execute("""
        SELECT d.id, u.name, d.specialization, d.experience_years, d.license_number 
        FROM doctors d 
        JOIN users u ON d.user_id = u.id 
        ORDER BY d.id DESC LIMIT 10
    """)
    doctors = cursor.fetchall()
    
    print(f"✅ Recent doctors ({len(doctors)} shown):")
    print(f"\n   {'ID':<4} {'Name':<25} {'Specialization':<20} {'Years':<7} {'License':<15}")
    print(f"   {'-'*4} {'-'*25} {'-'*20} {'-'*7} {'-'*15}")
    
    for doctor in doctors:
        doc_id = doctor[0]
        name = doctor[1][:25]
        spec = doctor[2][:20]
        years = doctor[3]
        license_num = (doctor[4] or "N/A")[:15]
        print(f"   {doc_id:<4} {name:<25} {spec:<20} {years:<7} {license_num:<15}")
    
    # ========================================================================
    # TEST 5: CHECK PATIENTS TABLE
    # ========================================================================
    print("\n[TEST 5] Checking Patients Table...")
    print("-" * 80)
    
    cursor.execute("""
        SELECT p.id, u.name, u.email, p.blood_group, p.gender 
        FROM patients p 
        JOIN users u ON p.user_id = u.id 
        ORDER BY p.id DESC LIMIT 10
    """)
    patients = cursor.fetchall()
    
    print(f"✅ Recent patients ({len(patients)} shown):")
    print(f"\n   {'ID':<4} {'Name':<30} {'Email':<35} {'Blood':<7} {'Gender':<8}")
    print(f"   {'-'*4} {'-'*30} {'-'*35} {'-'*7} {'-'*8}")
    
    for patient in patients:
        pat_id = patient[0]
        name = patient[1][:30]
        email = patient[2][:35]
        blood = (patient[3] or "N/A")[:7]
        gender = (patient[4] or "N/A")[:8]
        print(f"   {pat_id:<4} {name:<30} {email:<35} {blood:<7} {gender:<8}")
    
    # ========================================================================
    # TEST 6: CHECK LATEST USER (if registration worked)
    # ========================================================================
    if user_id:
        print("\n[TEST 6] Verifying Newly Registered User...")
        print("-" * 80)
        
        cursor.execute("""
            SELECT id, name, email, role, is_active, created_at 
            FROM users 
            WHERE id = ?
        """, (user_id,))
        
        user_record = cursor.fetchone()
        
        if user_record:
            print(f"✅ User found in database!")
            print(f"   ID: {user_record[0]}")
            print(f"   Name: {user_record[1]}")
            print(f"   Email: {user_record[2]}")
            print(f"   Role: {user_record[3]}")
            print(f"   Active: {'Yes' if user_record[4] else 'No'}")
            print(f"   Created: {user_record[5]}")
            
            # Check for corresponding patient/doctor
            if user_record[3] == 'patient':
                cursor.execute("SELECT id FROM patients WHERE user_id = ?", (user_id,))
                patient = cursor.fetchone()
                if patient:
                    print(f"   ✅ Patient profile created (ID: {patient[0]})")
                else:
                    print(f"   ❌ No patient profile found")
            elif user_record[3] == 'doctor':
                cursor.execute("SELECT id FROM doctors WHERE user_id = ?", (user_id,))
                doctor = cursor.fetchone()
                if doctor:
                    print(f"   ✅ Doctor profile created (ID: {doctor[0]})")
                else:
                    print(f"   ❌ No doctor profile found")
        else:
            print(f"❌ Registered user not found in database!")
    
    conn.close()
    
except sqlite3.Error as e:
    print(f"❌ Database Error: {str(e)}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("""
✅ DATABASE LOCATIONS:
   - SQLite DB: e:\\project\\POC 1st\\backend\\hospital.db
   - Can view with any SQLite client (see below)

📊 HOW TO VIEW DATABASE:
   
   Option 1: Using DBeaver (GUI - Recommended)
   --------------------------------------------
   1. Download DBeaver: https://dbeaver.io/
   2. Install and run it
   3. Click "New Database Connection"
   4. Select "SQLite"
   5. Choose file: e:\\project\\POC 1st\\backend\\hospital.db
   6. Browse tables, see all data visually

   Option 2: Using Python
   -----------------------
   1. Install sqlite3: pip install sqlite3
   2. Run this script again
   3. See all users, doctors, patients

   Option 3: Using Command Line
   ----------------------------
   cd "e:\\project\\POC 1st\\backend"
   sqlite3 hospital.db
   > SELECT * FROM users;
   > SELECT * FROM doctors;
   > SELECT * FROM patients;
""")
