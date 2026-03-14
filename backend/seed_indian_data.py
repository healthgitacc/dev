#!/usr/bin/env python3
"""
Seed script: Add 8 records each to doctors, patients, appointments, medical_records.
Uses Indian names. Does not add to hospitals table.
Creates users only as required for doctor/patient FK (8 doctor users + 8 patient users).
"""
import os
import random
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Indian names
DOCTOR_NAMES = [
    "Dr. Rajesh Kumar",
    "Dr. Priya Sharma",
    "Dr. Amit Patel",
    "Dr. Sneha Reddy",
    "Dr. Vikram Singh",
    "Dr. Ananya Iyer",
    "Dr. Arjun Nair",
    "Dr. Kavitha Menon",
]
PATIENT_NAMES = [
    "Suresh Gupta",
    "Lakshmi Venkatesh",
    "Ramesh Joshi",
    "Meera Krishnan",
    "Deepak Rao",
    "Pooja Desai",
    "Karthik Pillai",
    "Divya Nambiar",
]
SPECIALIZATIONS = [
    "Cardiology",
    "Dermatology",
    "General Medicine",
    "Pediatrics",
    "Orthopedics",
    "Neurology",
    "Psychiatry",
    "Pulmonology",
]
DISEASES = [
    "Hypertension",
    "Type 2 Diabetes",
    "Upper Respiratory Infection",
    "Migraine",
    "Acute Gastritis",
    "Anxiety Disorder",
    "Osteoarthritis",
    "Asthma",
]
BLOOD_GROUPS = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
GENDERS = ["male", "female"]


def run_seed():
    from app.core.session import SessionLocal
    from app.core.security import PasswordManager
    from app.models import User, Doctor, Patient, Appointment, MedicalRecord
    from app.models.user import UserRole

    db = SessionLocal()
    default_password_hash = PasswordManager.hash_password("Seed@123")

    try:
        # 1. Get or create 8 users (doctor role) with Indian names
        doctor_users = []
        for i, name in enumerate(DOCTOR_NAMES):
            email = f"doctor.seed{i+1}@hospital.in"
            u = db.query(User).filter(User.email == email).first()
            if not u:
                u = User(
                    name=name,
                    email=email,
                    phone=f"+91-98765-4{i:04d}1",
                    password_hash=default_password_hash,
                    role=UserRole.DOCTOR.value,
                    is_active=True,
                )
                db.add(u)
                db.flush()
            doctor_users.append(u)

        # 2. Get or create 8 users (patient role) with Indian names
        patient_users = []
        for i, name in enumerate(PATIENT_NAMES):
            email = f"patient.seed{i+1}@hospital.in"
            u = db.query(User).filter(User.email == email).first()
            if not u:
                u = User(
                    name=name,
                    email=email,
                    phone=f"+91-98765-4{i:04d}2",
                    password_hash=default_password_hash,
                    role=UserRole.PATIENT.value,
                    is_active=True,
                )
                db.add(u)
                db.flush()
            patient_users.append(u)

        db.commit()
        for u in doctor_users + patient_users:
            db.refresh(u)

        # 3. Add 8 doctors
        doctors = []
        for i, (user, name) in enumerate(zip(doctor_users, DOCTOR_NAMES)):
            d = db.query(Doctor).filter(Doctor.user_id == user.id).first()
            if not d:
                d = Doctor(
                    user_id=user.id,
                    name=name,
                    specialization=SPECIALIZATIONS[i],
                    experience_years=random.randint(3, 25),
                    license_number=f"LIC-IN-{1000 + i}",
                )
                db.add(d)
                db.flush()
            doctors.append(d)

        # 4. Add 8 patients
        patients = []
        for i, (user, name) in enumerate(zip(patient_users, PATIENT_NAMES)):
            p = db.query(Patient).filter(Patient.user_id == user.id).first()
            if not p:
                p = Patient(
                    user_id=user.id,
                    age=random.randint(22, 70),
                    gender=random.choice(GENDERS),
                    blood_group=BLOOD_GROUPS[i],
                    medical_history="None" if i % 2 == 0 else "Previous checkups only",
                )
                db.add(p)
                db.flush()
            patients.append(p)

        db.commit()
        for d in doctors:
            db.refresh(d)
        for p in patients:
            db.refresh(p)

        # 5. Add 8 appointments (raw SQL with cast for PostgreSQL enum status column if needed)
        from sqlalchemy import text
        status_values = ["scheduled", "completed", "cancelled", "no_show"]
        added_apt = 0
        now = datetime.now(timezone.utc)
        dialect = db.get_bind().dialect.name
        for _ in range(20):
            if added_apt >= 8:
                break
            doctor = random.choice(doctors)
            patient = random.choice(patients)
            apt_date = now + timedelta(days=random.randint(-30, 60))
            apt_date = apt_date.replace(hour=random.randint(9, 16), minute=0, second=0, microsecond=0)
            if apt_date.tzinfo:
                apt_date = apt_date.replace(tzinfo=None)
            exists = db.query(Appointment).filter(
                Appointment.doctor_id == doctor.id,
                Appointment.patient_id == patient.id,
                Appointment.appointment_date == apt_date,
            ).first()
            if not exists:
                st = random.choice(status_values)
                if dialect == "postgresql":
                    db.execute(
                        text(
                            "INSERT INTO appointments (doctor_id, patient_id, appointment_date, duration_minutes, status, notes, created_at, updated_at) "
                            "VALUES (:did, :pid, :dt, :dur, CAST(:status AS appointmentstatus), :notes, :created, :updated)"
                        ),
                        {
                            "did": doctor.id,
                            "pid": patient.id,
                            "dt": apt_date,
                            "dur": random.choice([30, 45, 60]),
                            "status": st,
                            "notes": "Follow-up" if added_apt % 2 else None,
                            "created": now.replace(tzinfo=None) if now.tzinfo else now,
                            "updated": now.replace(tzinfo=None) if now.tzinfo else now,
                        },
                    )
                else:
                    db.add(Appointment(
                        doctor_id=doctor.id,
                        patient_id=patient.id,
                        appointment_date=apt_date,
                        duration_minutes=random.choice([30, 45, 60]),
                        status=st,
                        notes="Follow-up" if added_apt % 2 else None,
                    ))
                added_apt += 1
        db.commit()

        # 6. Add 8 medical records
        now = datetime.now(timezone.utc)
        for i in range(8):
            doctor = random.choice(doctors)
            patient = random.choice(patients)
            disease = DISEASES[i]
            follow = now + timedelta(days=random.randint(7, 90))
            if follow.tzinfo:
                follow = follow.replace(tzinfo=None)
            db.add(MedicalRecord(
                patient_id=patient.id,
                doctor_id=doctor.id,
                disease_name=disease,
                diagnosis=f"Diagnosed {disease}. Recommended lifestyle changes and medication.",
                prescription_text="As prescribed by doctor" if i % 2 else "Paracetamol 500mg PRN",
                dosage="As directed",
                follow_up_date=follow,
                notes="Patient record.",
            ))
        db.commit()

        print("Seeded: 8 doctors, 8 patients, 8 appointments, 8 medical_records (Indian names).")
        print("No records added to hospitals table.")
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        run_seed()
        print("Done.")
    except Exception as e:
        print(f"Seed failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
