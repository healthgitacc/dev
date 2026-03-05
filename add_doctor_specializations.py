#!/usr/bin/env python3
"""
Add dummy specializations and experience years to existing doctors in the database.
"""
import os
import sys
os.chdir('E:\\project\\hospital\\backend')
sys.path.insert(0, 'E:\\project\\hospital\\backend')

from sqlalchemy import create_engine, text
from datetime import datetime

# Use SQLite database (default)
DATABASE_URL = "sqlite:///./hospital.db"

# Doctor data to update
DOCTOR_UPDATES = [
    {"id": 1, "specialization": "Cardiology", "experience_years": 12, "license": "MD-CAR-001"},
    {"id": 2, "specialization": "Endocrinology", "experience_years": 10, "license": "MD-END-001"},
    {"id": 3, "specialization": "General Practice", "experience_years": 8, "license": "MD-GP-001"},
    {"id": 4, "specialization": "Neurology", "experience_years": 14, "license": "MD-NEU-001"},
    {"id": 5, "specialization": "Orthopedics", "experience_years": 11, "license": "MD-ORT-001"},
    {"id": 6, "specialization": "Psychiatry", "experience_years": 9, "license": "MD-PSY-001"},
    {"id": 7, "specialization": "Pediatrics", "experience_years": 7, "license": "MD-PED-001"},
    {"id": 8, "specialization": "Dermatology", "experience_years": 13, "license": "MD-DER-001"},
    {"id": 9, "specialization": "Ophthalmology", "experience_years": 10, "license": "MD-OPH-001"},
    {"id": 10, "specialization": "ENT", "experience_years": 11, "license": "MD-ENT-001"},
]

def main():
    print("=" * 80)
    print("ADDING DOCTOR SPECIALIZATIONS AND EXPERIENCE YEARS")
    print("=" * 80)

    try:
        engine = create_engine(DATABASE_URL)
        print("[OK] Connected to SQLite database")
    except Exception as e:
        print(f"[FAIL] Failed to connect: {e}")
        return

    try:
        # Direct SQL update approach
        with engine.connect() as connection:
            # First check how many doctors exist
            result = connection.execute(text("SELECT COUNT(*) FROM doctors"))
            doctor_count = result.scalar()
            print(f"\n[OK] Found {doctor_count} doctors in database")

            # Update each doctor
            updated = 0
            for update_data in DOCTOR_UPDATES:
                try:
                    # Update the doctor
                    connection.execute(text("""
                        UPDATE doctors 
                        SET specialization = :spec, 
                            experience_years = :exp, 
                            license_number = :license,
                            updated_at = :now
                        WHERE id = :id
                    """), {
                        "spec": update_data["specialization"],
                        "exp": update_data["experience_years"],
                        "license": update_data["license"],
                        "id": update_data["id"],
                        "now": datetime.utcnow()
                    })
                    connection.commit()
                    print(f"  [+] Doctor {update_data['id']}: {update_data['specialization']} ({update_data['experience_years']} yrs)")
                    updated += 1
                except Exception as e:
                    print(f"  [-] Doctor {update_data['id']}: {e}")

            print(f"\n[OK] Updated {updated} doctors successfully!")

            # Display verification
            print("\n[VERIFICATION] Updated Doctors:\n")
            result = connection.execute(text("""
                SELECT d.id, u.name, d.specialization, d.experience_years, d.license_number
                FROM doctors d
                LEFT JOIN users u ON d.user_id = u.id
                ORDER BY d.id
                LIMIT 15
            """))
            
            for i, row in enumerate(result, 1):
                doc_id, name, spec, exp, license_num = row
                print(f"{i:2d}. {name or f'Doctor {doc_id}':<30s} | {spec:<20s} | {exp} years | {license_num or 'N/A'}")

        print("\n" + "=" * 80)
        print("[OK] DOCTOR DATA UPDATE COMPLETE!")
        print("=" * 80)

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
