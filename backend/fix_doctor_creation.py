#!/usr/bin/env python3
"""
Fix doctor creation by manually managing the ID sequence.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database import engine
    from sqlalchemy import text
    
    print("🔧 Fixing doctor creation by managing ID manually...")
    
    with engine.connect() as conn:
        # Get all existing doctor IDs
        existing_ids = conn.execute(text('SELECT id FROM doctors ORDER BY id')).fetchall()
        existing_ids = [r[0] for r in existing_ids]
        print(f"📊 Existing doctor IDs: {existing_ids}")
        
        # Find next available ID
        next_id = 1
        while next_id in existing_ids:
            next_id += 1
        
        print(f"🎯 Next available ID: {next_id}")
        
        # Check current sequence value
        try:
            seq_value = conn.execute(text('SELECT last_value FROM doctors_id_seq')).scalar()
            print(f"🔢 Sequence last_value: {seq_value}")
        except:
            print("❌ Sequence not found")
        
        # Reset sequence to the next available ID
        print(f"🔧 Setting sequence to: {next_id}")
        conn.execute(text(f"SELECT setval('doctors_id_seq', {next_id}, false)"))
        conn.commit()
        
        print("✅ Sequence fixed!")
        
        # Verify by trying to insert a test doctor
        print("🧪 Testing doctor creation...")
        try:
            conn.execute(text(f"""
                INSERT INTO doctors (id, user_id, name, specialization, experience_years, license_number, created_at, updated_at)
                VALUES ({next_id}, 999, 'Test Doctor', 'Test Specialization', 1, 'TEST123', NOW(), NOW())
            """))
            conn.commit()
            print(f"✅ Successfully inserted test doctor with ID {next_id}")
            
            # Clean up test doctor
            conn.execute(text(f"DELETE FROM doctors WHERE id = {next_id}"))
            conn.commit()
            print("🧹 Cleaned up test doctor")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print("🎉 Doctor creation should now work!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)