#!/usr/bin/env python3
"""
Migration: Add departments and department_admin support.
- Creates departments table.
- Adds department_id, created_by_id to users.
- Adds department_id to doctors.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_migration(engine):
    from sqlalchemy import text
    from sqlalchemy.engine import reflection

    import app.database  # noqa: F401 - register models

    inspector = reflection.Inspector.from_engine(engine)
    dialect = engine.dialect.name

    with engine.begin() as conn:
        if "departments" not in inspector.get_table_names():
            from app.models.department import Department
            Department.__table__.create(engine, checkfirst=True)
            print("Created table departments")
        else:
            print("Table departments already exists")

    inspector = reflection.Inspector.from_engine(engine)
    user_cols = [c["name"] for c in inspector.get_columns("users")]
    doctor_cols = [c["name"] for c in inspector.get_columns("doctors")]

    with engine.begin() as conn:
        if "department_id" not in user_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_department_id ON users(department_id)"))
            print("Added users.department_id")
        if "created_by_id" not in user_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_created_by_id ON users(created_by_id)"))
            print("Added users.created_by_id")

        if "department_id" not in doctor_cols:
            conn.execute(text("ALTER TABLE doctors ADD COLUMN department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_doctors_department_id ON doctors(department_id)"))
            print("Added doctors.department_id")

    # Seed default departments (Ortho, Neuro, Uro) for each existing hospital
    from app.models import Hospital
    from sqlalchemy.orm import Session
    from app.services.department_service import DepartmentService
    session = Session(engine)
    try:
        dept_service = DepartmentService(session)
        for hospital in session.query(Hospital).all():
            dept_service.ensure_default_departments(hospital.id)
        session.commit()
        print("Seeded default departments (Ortho, Neuro, Uro) for existing hospitals.")
    except Exception as e:
        session.rollback()
        print(f"Note: Could not seed departments: {e}")
    finally:
        session.close()

    print("Migration completed.")


if __name__ == "__main__":
    from app.core.engine import engine
    try:
        run_migration(engine)
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
