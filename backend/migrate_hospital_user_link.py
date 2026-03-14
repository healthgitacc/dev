#!/usr/bin/env python3
"""
Migration: Move user-hospital link from users.hospital_id to hospital_users table.

- Core interconnected tables: users, doctors, patients, appointments, medical_records.
- hospitals table is separate (super_owner only); link via hospital_users.

Steps:
1. Create hospital_users table via SQLAlchemy metadata.
2. Copy (user_id, hospital_id) from users where hospital_id IS NOT NULL into hospital_users.
3. Drop column hospital_id and its FK from users.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_migration(engine):
    from sqlalchemy import text
    from sqlalchemy.engine import reflection

    # Ensure all models (including HospitalUser) are registered
    import app.database  # noqa: F401

    inspector = reflection.Inspector.from_engine(engine)
    dialect = engine.dialect.name

    with engine.begin() as conn:
        # 1. Create hospital_users if not exists (use metadata for portability)
        if "hospital_users" not in inspector.get_table_names():
            from app.models.base import Base
            from app.models.hospital_user import HospitalUser
            HospitalUser.__table__.create(engine, checkfirst=True)
            print("Created table hospital_users")
        else:
            print("Table hospital_users already exists")

    inspector = reflection.Inspector.from_engine(engine)
    columns = [c["name"] for c in inspector.get_columns("users")]
    if "hospital_id" not in columns:
        print("Column users.hospital_id already removed; nothing to migrate.")
        return

    with engine.begin() as conn:
        # 2. Copy existing assignments (avoid duplicate if unique exists)
        if dialect == "postgresql":
            conn.execute(text("""
                INSERT INTO hospital_users (hospital_id, user_id)
                SELECT hospital_id, id FROM users WHERE hospital_id IS NOT NULL
                ON CONFLICT (hospital_id, user_id) DO NOTHING
            """))
        else:
            conn.execute(text("""
                INSERT OR IGNORE INTO hospital_users (hospital_id, user_id)
                SELECT hospital_id, id FROM users WHERE hospital_id IS NOT NULL
            """))
        print("Migrated user-hospital links to hospital_users")

        # 3. Drop FK (postgresql) then column
        if dialect == "postgresql":
            conn.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_hospital_id_fkey"))
            conn.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS fk_users_hospital_id"))
        conn.execute(text("ALTER TABLE users DROP COLUMN hospital_id"))
        print("Dropped users.hospital_id")


if __name__ == "__main__":
    from app.core.engine import engine

    try:
        run_migration(engine)
        print("Migration completed.")
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
