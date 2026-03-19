#!/usr/bin/env python3
"""
Seed script: Linked dummy data for Create Department Admin flow.

Tables filled (in order):
  hospitals     -> 1 hospital (XYZ Hospital)
  hospital_users -> links hospital_admin + department_admins to hospital
  departments   -> Ortho, Neuro, Cardiology, Uro (for that hospital)
  users         -> 1 hospital_admin (if missing) + 3 department admins

After running:
- Login as Hospital Admin (XYZ Hospital) and see departments in Create Department Admin page.
- Login as any Department Admin (ortho_admin, cardio_admin, neuro_admin) with password Seed@123.
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Default password for all seeded users (change in production)
SEED_PASSWORD = "Seed@123"

# XYZ Hospital (hospital admin) - must exist in users table or we create one
HOSPITAL_ADMIN_EMAIL = "hospitaadmin@example.com"
HOSPITAL_ADMIN_NAME = "XYZ Hospital"
HOSPITAL_ADMIN_PHONE = "+917676454233"

# Department names for the hospital
DEPARTMENT_NAMES = ["Ortho", "Neuro", "Cardiology", "Uro"]

# Department admins to create: (name, email, department_name)
DEPARTMENT_ADMINS = [
    ("Ortho Admin", "ortho_admin@xyz.com", "Ortho"),
    ("Cardio Admin", "cardio_admin@xyz.com", "Cardiology"),
    ("Neuro Admin", "neuro_admin@xyz.com", "Neuro"),
]

DOCTOR_DEPARTMENT_MAP = {
    "Cardiology": "Cardiology",
    "Orthopedics": "Ortho",
    "Neurology": "Neuro",
}


def run_seed():
    from app.core.engine import create_sqlalchemy_engine
    from sqlalchemy import text
    engine = create_sqlalchemy_engine()
    from app.core.security import PasswordManager
    from app.models import (
        User,
        Hospital,
        HospitalUser,
        Department,
        Doctor,
    )
    from app.models.user import UserRole
    from app.models.hospital import HospitalStatus
    from sqlalchemy.orm import Session

    # Ensure PostgreSQL enum has hospital_admin and department_admin (if DB uses enum)
    if engine.dialect.name == "postgresql":
        with engine.connect() as conn:
            for role_value in ("hospital_admin", "department_admin"):
                try:
                    conn.execute(text(f"ALTER TYPE userrole ADD VALUE IF NOT EXISTS '{role_value}'"))
                except Exception:
                    pass
            conn.commit()

    db = Session(engine)
    password_hash = PasswordManager.hash_password(SEED_PASSWORD)

    try:
        # 1. Get or create Hospital Admin user (XYZ Hospital)
        hospital_admin = db.query(User).filter(User.email == HOSPITAL_ADMIN_EMAIL).first()
        if not hospital_admin:
            hospital_admin = User(
                name=HOSPITAL_ADMIN_NAME,
                email=HOSPITAL_ADMIN_EMAIL,
                phone=HOSPITAL_ADMIN_PHONE,
                password_hash=password_hash,
                role=UserRole.HOSPITAL_ADMIN.value,
                is_active=True,
            )
            db.add(hospital_admin)
            db.flush()
            print(f"  Created user: {hospital_admin.email} (hospital_admin)")
        else:
            hospital_admin.password_hash = password_hash
            print(f"  Using existing user: {hospital_admin.email} (hospital_admin), password set to SEED")

        # 2. Get or create Hospital row (XYZ Hospital)
        hospital_email = "xyz.hospital@careflow.internal"
        hospital = db.query(Hospital).filter(Hospital.email == hospital_email).first()
        if not hospital:
            hospital = Hospital(
                name=HOSPITAL_ADMIN_NAME,
                email=hospital_email,
                phone=HOSPITAL_ADMIN_PHONE,
                address=None,
                status=HospitalStatus.ACTIVE,
            )
            db.add(hospital)
            db.flush()
            print(f"  Created hospital: {hospital.name} (id={hospital.id})")
        else:
            print(f"  Using existing hospital: {hospital.name} (id={hospital.id})")

        # 3. Link Hospital Admin to Hospital (hospital_users)
        hu_exists = db.query(HospitalUser).filter(
            HospitalUser.hospital_id == hospital.id,
            HospitalUser.user_id == hospital_admin.id,
        ).first()
        if not hu_exists:
            db.add(HospitalUser(hospital_id=hospital.id, user_id=hospital_admin.id))
            db.flush()
            print(f"  Linked hospital_admin to hospital (hospital_users)")
        else:
            print(f"  hospital_admin already linked (hospital_users)")

        # 4. Create departments (Ortho, Neuro, Cardiology, Uro)
        dept_by_name = {}
        for name in DEPARTMENT_NAMES:
            existing = db.query(Department).filter(
                Department.hospital_id == hospital.id,
                Department.name == name,
            ).first()
            if not existing:
                dept = Department(hospital_id=hospital.id, name=name)
                db.add(dept)
                db.flush()
                dept_by_name[name] = dept
                print(f"  Created department: {name} (id={dept.id})")
            else:
                dept_by_name[name] = existing
                print(f"  Using existing department: {name} (id={existing.id})")

        # 5. Create Department Admin users and link to hospital + department
        for name, email, dept_name in DEPARTMENT_ADMINS:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                dept = dept_by_name.get(dept_name)
                if not dept:
                    print(f"  Skip {email}: department '{dept_name}' not found")
                    continue
                user = User(
                    name=name,
                    email=email,
                    phone=None,
                    password_hash=password_hash,
                    role=UserRole.DEPARTMENT_ADMIN.value,
                    is_active=True,
                    department_id=dept.id,
                    created_by_id=hospital_admin.id,
                )
                db.add(user)
                db.flush()
                db.add(HospitalUser(hospital_id=hospital.id, user_id=user.id))
                db.flush()
                print(f"  Created department admin: {email} -> {dept_name}")
            else:
                print(f"  Using existing user: {email}")

        # 6. Assign existing doctors to departments so department admins can see them
        linked_doctors = 0
        assigned_doctors = 0
        doctors = db.query(Doctor).all()
        for doctor in doctors:
            dept_name = DOCTOR_DEPARTMENT_MAP.get((doctor.specialization or "").strip())
            if not dept_name:
                continue
            dept = dept_by_name.get(dept_name)
            if not dept:
                continue
            if doctor.department_id != dept.id:
                doctor.department_id = dept.id
                assigned_doctors += 1
            if doctor.user_id and not db.query(HospitalUser).filter(
                HospitalUser.hospital_id == hospital.id,
                HospitalUser.user_id == doctor.user_id,
            ).first():
                db.add(HospitalUser(hospital_id=hospital.id, user_id=doctor.user_id))
                linked_doctors += 1

        db.commit()
        print("\n" + "=" * 60)
        print("SEED DONE. Table relationships:")
        print("  hospitals      : 1 row (XYZ Hospital)")
        print("  hospital_users : hospital_admin + 3 department admins + linked doctors")
        print("  departments    : Ortho, Neuro, Cardiology, Uro")
        print("  users          : 1 hospital_admin + 3 department_admins (created_by = hospital_admin)")
        print(f"  doctors        : {assigned_doctors} doctors assigned to departments, {linked_doctors} linked to hospital")
        print("=" * 60)
        print("LOGIN CREDENTIALS (all use password: " + SEED_PASSWORD + "):")
        print(f"  Hospital Admin  : {HOSPITAL_ADMIN_EMAIL}")
        print(f"  Department Admins (same password):")
        for _, email, dept in DEPARTMENT_ADMINS:
            print(f"    - {email} -> {dept}")
        print("=" * 60)
        return True
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding linked data for Create Department Admin...")
    run_seed()
