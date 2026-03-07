#!/usr/bin/env python3
"""
Script to fix PostgreSQL sequence issues.
Resets the sequence for doctors table to prevent duplicate key errors.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text

def fix_doctors_sequence():
    """Fix the doctors table sequence."""
    try:
        with engine.connect() as conn:
            # Reset the sequence for doctors table
            conn.execute(text('''
                SELECT setval(pg_get_serial_sequence('doctors', 'id'), 
                             COALESCE((SELECT MAX(id) FROM doctors), 0) + 1);
            '''))
            conn.commit()
            print("✅ Doctors sequence reset successfully!")
            
            # Also fix users sequence just in case
            conn.execute(text('''
                SELECT setval(pg_get_serial_sequence('users', 'id'), 
                             COALESCE((SELECT MAX(id) FROM users), 0) + 1);
            '''))
            conn.commit()
            print("✅ Users sequence reset successfully!")
            
    except Exception as e:
        print(f"❌ Error fixing sequence: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Fixing PostgreSQL sequences...")
    success = fix_doctors_sequence()
    if success:
        print("🎉 All sequences fixed!")
    else:
        print("💥 Failed to fix sequences!")
        sys.exit(1)