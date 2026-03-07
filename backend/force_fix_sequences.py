#!/usr/bin/env python3
"""
Force fix PostgreSQL sequences - more robust version.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database import engine
    from sqlalchemy import text
    
    print("🔧 Force fixing PostgreSQL sequences...")
    
    with engine.connect() as conn:
        # Force reset doctors sequence
        print("📊 Checking current max IDs...")
        max_doctor_id = conn.execute(text('SELECT COALESCE(MAX(id), 0) FROM doctors')).scalar()
        max_user_id = conn.execute(text('SELECT COALESCE(MAX(id), 0) FROM users')).scalar()
        
        print(f"Current max doctor ID: {max_doctor_id}")
        print(f"Current max user ID: {max_user_id}")
        
        # Force reset sequences with explicit values
        new_doctor_seq = max_doctor_id + 1
        new_user_seq = max_user_id + 1
        
        print(f"🔧 Setting doctors sequence to: {new_doctor_seq}")
        print(f"🔧 Setting users sequence to: {new_user_seq}")
        
        # Reset sequences
        conn.execute(text(f"SELECT setval('doctors_id_seq', {new_doctor_seq}, false)"))
        conn.execute(text(f"SELECT setval('users_id_seq', {new_user_seq}, false)"))
        conn.commit()
        
        print("✅ Sequences reset successfully!")
        
        # Verify the fix
        next_doctor_id = conn.execute(text('SELECT nextval(\'doctors_id_seq\')')).scalar()
        next_user_id = conn.execute(text('SELECT nextval(\'users_id_seq\')')).scalar()
        
        print(f"🎯 Next doctor ID will be: {next_doctor_id}")
        print(f"🎯 Next user ID will be: {next_user_id}")
        
        # Reset back to the correct value
        conn.execute(text(f"SELECT setval('doctors_id_seq', {next_doctor_id}, false)"))
        conn.execute(text(f"SELECT setval('users_id_seq', {next_user_id}, false)"))
        conn.commit()
        
        print("✅ Sequences verified and fixed!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("🎉 Database sequences fixed!")