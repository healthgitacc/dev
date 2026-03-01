import sqlite3

db_path = r"e:\project\POC 1st\backend\hospital.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n" + "="*80)
print("LATEST USERS (Newest First)")
print("="*80)
cursor.execute("SELECT id, name, email, role, created_at FROM users ORDER BY id DESC LIMIT 10")
for row in cursor.fetchall():
    print(f"ID: {row[0]:<3} | Name: {row[1]:<30} | Email: {row[2]:<35} | Role: {row[3]:<8} | Created: {row[4]}")

print("\n" + "="*80)
print("LATEST DOCTORS")
print("="*80)
cursor.execute("""
    SELECT d.id, u.name, u.email, d.specialization, d.license_number 
    FROM doctors d 
    JOIN users u ON d.user_id = u.id 
    ORDER BY d.id DESC LIMIT 5
""")
for row in cursor.fetchall():
    print(f"ID: {row[0]:<3} | Name: {row[1]:<30} | Email: {row[2]:<35} | Specialization: {row[3]:<15} | License: {row[4]}")

print("\n" + "="*80)
print("LATEST PATIENTS")
print("="*80)
cursor.execute("""
    SELECT p.id, u.name, u.email, p.blood_group, p.gender 
    FROM patients p 
    JOIN users u ON p.user_id = u.id 
    ORDER BY p.id DESC LIMIT 5
""")
for row in cursor.fetchall():
    blood = row[3] if row[3] else "N/A"
    gender = row[4] if row[4] else "N/A"
    print(f"ID: {row[0]:<3} | Name: {row[1]:<30} | Email: {row[2]:<35} | Blood: {blood:<5} | Gender: {gender}")

print("\n" + "="*80)
print("LATEST APPOINTMENTS")
print("="*80)
cursor.execute("""
    SELECT a.id, p.name as patient_name, d.name as doctor_name, a.appointment_date, a.status
    FROM appointments a
    JOIN patients pat ON a.patient_id = pat.id
    JOIN users p ON pat.user_id = p.id
    JOIN doctors doc ON a.doctor_id = doc.id
    JOIN users d ON doc.user_id = d.id
    ORDER BY a.id DESC LIMIT 10
""")
appointments = cursor.fetchall()
if appointments:
    for row in appointments:
        print(f"ID: {row[0]:<3} | Patient: {row[1]:<30} | Doctor: {row[2]:<30} | DateTime: {row[3]:<20} | Status: {row[4]}")
else:
    print("No appointments found yet")

print("\n" + "="*80)
print("APPOINTMENT COUNT SUMMARY")
print("="*80)
cursor.execute("SELECT COUNT(*) FROM appointments")
total = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'confirmed'")
confirmed = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'pending'")
pending = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'cancelled'")
cancelled = cursor.fetchone()[0]
print(f"Total Appointments: {total} | Confirmed: {confirmed} | Pending: {pending} | Cancelled: {cancelled}")

conn.close()
print("\n")
