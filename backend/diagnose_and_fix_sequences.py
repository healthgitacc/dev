#!/usr/bin/env python3
"""
Comprehensive diagnostic and fix script for PostgreSQL sequence issues.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database import engine
    from sqlalchemy import text
    
    print("🔍 Comprehensive database sequence diagnosis and fix...")
    
    with engine.connect() as conn:
        # Get all doctor IDs
        doctor_ids = conn.execute(text('SELECT id FROM doctors ORDER BY id')).fetchall()
        doctor_ids = [r[0] for r in doctor_ids]
        print(f"📊 All doctor IDs: {doctor_ids}")
        
        # Get all user IDs
        user_ids = conn.execute(text('SELECT id FROM users ORDER BY id')).fetchall()
        user_ids = [r[0] for r in user_ids]
        print(f"📊 All user IDs: {user_ids}")
        
        # Check sequence values
        doctor_seq = conn.execute(text('SELECT last_value FROM doctors_id_seq')).scalar()
        user_seq = conn.execute(text('SELECT last_value FROM users_id_seq')).scalar()
        
        print(f"🔢 Doctors sequence last_value: {doctor_seq}")
        print(f"🔢 Users sequence last_value: {user_seq}")
        
        # Check max IDs
        max_doctor_id = conn.execute(text('SELECT COALESCE(MAX(id), 0) FROM doctors')).scalar()
        max_user_id = conn.execute(text('SELECT COALESCE(MAX(id), 0) FROM users')).scalar()
        
        print(f"📈 Max doctor ID: {max_doctor_id}")
        print(f"📈 Max user ID: {max_user_id}")
        
        # Analyze sequence issues
        print("\n🔍 Sequence Analysis:")
        
        if doctor_seq <= max_doctor_id:
            print(f"❌ Doctors sequence ({doctor_seq}) is behind max ID ({max_doctor_id})")
            new_doctor_seq = max_doctor_id + 1
            print(f"🔧 Fixing doctors sequence to: {new_doctor_seq}")
            conn.execute(text(f"SELECT setval('doctors_id_seq', {new_doctor_seq}, false)"))
        else:
            print(f"✅ Doctors sequence ({doctor_seq}) is ahead of max ID ({max_doctor_id})")
        
        if user_seq <= max_user_id:
            print(f"❌ Users sequence ({user_seq}) is behind max ID ({max_user_id})")
            new_user_seq = max_user_id + 1
            print(f"🔧 Fixing users sequence to: {new_user_seq}")
            conn.execute(text(f"SELECT setval('users_id_seq', {new_user_seq}, false)"))
        else:
            print(f"✅ Users sequence ({user_seq}) is ahead of max ID ({max_user_id})")
        
        conn.commit()
        
        # Verify the fix
        print("\n✅ Verification:")
        next_doctor_id = conn.execute(text('SELECT nextval(\'doctors_id_seq\')')).scalar()
        next_user_id = conn.execute(text('SELECT nextval(\'users_id_seq\')')).scalar()
        
        print(f"🎯 Next doctor ID will be: {next_doctor_id}")
        print(f"🎯 Next user ID will be: {next_user_id}")
        
        # Reset sequences to correct values
        conn.execute(text(f"SELECT setval('doctors_id_seq', {next_doctor_id}, false)"))
        conn.execute(text(f"SELECT setval('users_id_seq', {next_user_id}, false)"))
        conn.commit()
        
        print("✅ Sequences verified and fixed!")
        
        # Final check
        final_doctor_seq = conn.execute(text('SELECT last_value FROM doctors_id_seq')).scalar()
        final_user_seq = conn.execute(text('SELECT last_value FROM users_id_seq')).scalar()
        
        print(f"\n🏁 Final doctors sequence: {final_doctor_seq}")
        print(f"🏁 Final users sequence: {final_user_seq}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("🎉 Database sequences diagnosed and fixed!")