#!/usr/bin/env python3
"""
Simple script to fix PostgreSQL sequence issues.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database import engine
    from sqlalchemy import text
    
    print("🔧 Fixing PostgreSQL sequences...")
    
    with engine.connect() as conn:
        # Check current max IDs
        max_doctor_id = conn.execute(text('SELECT COALESCE(MAX(id), 0) FROM doctors')).scalar()
        max_user_id = conn.execute(text('SELECT COALESCE(MAX(id), 0) FROM users')).scalar()
        
        print(f"📊 Current max doctor ID: {max_doctor_id}")
        print(f"📊 Current max user ID: {max_user_id}")
        
        # Reset sequences
        conn.execute(text(f"SELECT setval('doctors_id_seq', {max_doctor_id + 1})"))
        conn.execute(text(f"SELECT setval('users_id_seq', {max_user_id + 1})"))
        conn.commit()
        
        print("✅ Sequences reset successfully!")
        print(f"🎯 Next doctor ID will be: {max_doctor_id + 1}")
        print(f"🎯 Next user ID will be: {max_user_id + 1}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("🎉 Database sequences fixed!")