# Database schema – table connections

## Interconnected tables (core app)

These 5 tables are connected to each other; they form the main application data model.

| Table             | Connections |
|-------------------|-------------|
| **users**         | → doctors (1:1), → patients (1:1) |
| **doctors**       | → users, → appointments, → medical_records |
| **patients**      | → users, → appointments, → medical_records |
| **appointments**  | → doctors, → patients |
| **medical_records** | → doctors, → patients |

- **users**: base accounts (admin, doctor, patient, hospital_admin, etc.).
- **doctors**: `user_id` → users; has appointments and medical_records.
- **patients**: `user_id` → users; has appointments and medical_records.
- **appointments**: `doctor_id` → doctors, `patient_id` → patients.
- **medical_records**: `doctor_id` → doctors, `patient_id` → patients.

No foreign keys from these tables point to **hospitals**.

---

## Hospitals (super_owner only)

The **hospitals** table is separate and is used only by the super_owner (e.g. create/activate/deactivate hospitals).

Linking users (e.g. hospital admins) to hospitals is done only via the **hospital_users** association table:

| Table            | Role |
|------------------|------|
| **hospitals**    | Standalone; no FKs from users/doctors/patients/appointments/medical_records. |
| **hospital_users** | Association: `hospital_id` → hospitals, `user_id` → users. Used so super_owner can assign users (e.g. hospital_admin) to a hospital. |

So:

- **users**, **doctors**, **patients**, **appointments**, **medical_records** are interconnected.
- **hospitals** is separate and only referenced via **hospital_users**.

---

## Migration

If your database still has `users.hospital_id`:

```bash
cd backend
python migrate_hospital_user_link.py
```

This will create **hospital_users**, copy existing user–hospital links into it, and drop **users.hospital_id**.
