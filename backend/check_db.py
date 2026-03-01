#!/usr/bin/env python
"""Check database state"""
from app.database import SessionLocal
from app.models import User, Patient

db = SessionLocal()

# Get user 48
user = db.query(User).filter(User.id == 48).first()
print(f'User 48: {user.email if user else "NOT FOUND"}')

if user:
    # Check if patient exists for user 48
    patient = db.query(Patient).filter(Patient.user_id == 48).first()
    print(f'Patient for user 48: {patient.id if patient else "NOT FOUND"}')
    
    # Check doctor too
    doctor = db.query(User).filter(User.id == 48, User.doctor).first()
    print(f'Doctor for user 48: exists')

db.close()
