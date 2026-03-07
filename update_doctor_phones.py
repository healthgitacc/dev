#!/usr/bin/env python
"""Update doctor phone numbers to valid Twilio-compatible formats."""
import sys
sys.path.insert(0, 'backend')

from app.database import get_db, init_db
from app.models import Doctor, User
from sqlalchemy.orm import Session

# Initialize database if needed
init_db()

# Get database session
db = next(get_db())

# Doctor phone number updates (mapping by email to find the right records)
doctor_updates = {
    "dr.sarah.johnson@hospital.com": "+919876543201",
    "dr.james.wilson@hospital.com": "+919876543202",
    "dr.emily.chen@hospital.com": "+919876543203",
    "dr.michael.brown@hospital.com": "+919876543204",
    "dr.laura.martinez@hospital.com": "+919876543205",
}

try:
    updated_count = 0
    for email, new_phone in doctor_updates.items():
        # Find doctor by email
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"Found: {user.name} ({user.email})")
            print(f"  Old phone: {user.phone}")
            user.phone = new_phone
            print(f"  New phone: {new_phone}")
            updated_count += 1
        else:
            print(f"NOT FOUND: {email}")
    
    # Commit the changes
    db.commit()
    print(f"\n✅ Updated {updated_count} doctor phone numbers successfully!")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error: {str(e)}")
    sys.exit(1)
finally:
    db.close()
