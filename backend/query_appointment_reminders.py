#!/usr/bin/env python3
"""
Inspect appointment reminder rows and reply status from the database.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Query appointment reminders")
    parser.add_argument("--status", help="Filter by reminder status")
    parser.add_argument("--phone", help="Filter by patient phone (partial allowed)")
    parser.add_argument("--limit", type=int, default=10, help="Max rows to print")
    args = parser.parse_args()

    from sqlalchemy.orm import Session
    from app.core.engine import create_sqlalchemy_engine
    from app.models import AppointmentReminder

    engine = create_sqlalchemy_engine()
    db = Session(engine)

    try:
        query = db.query(AppointmentReminder).order_by(AppointmentReminder.updated_at.desc())
        if args.status:
            query = query.filter(AppointmentReminder.status == args.status)
        if args.phone:
            phone_filter = "".join(ch for ch in args.phone if ch.isdigit())
            query = query.filter(AppointmentReminder.phone_number.contains(phone_filter))

        reminders = query.limit(max(1, args.limit)).all()

        if not reminders:
            print("No appointment reminders found.")
            return 0

        for reminder in reminders:
            appointment = reminder.appointment
            patient_name = appointment.patient.user.name if appointment and appointment.patient and appointment.patient.user else "Unknown"
            doctor_name = appointment.doctor.name if appointment and appointment.doctor else "Unknown"
            appointment_date = appointment.appointment_date.isoformat() if appointment else "-"
            print("=" * 80)
            print(f"Reminder ID     : {reminder.id}")
            print(f"Appointment ID  : {reminder.appointment_id}")
            print(f"Patient         : {patient_name}")
            print(f"Phone           : {reminder.phone_number}")
            print(f"Doctor          : {doctor_name}")
            print(f"Appointment Date: {appointment_date}")
            print(f"Status          : {reminder.status}")
            print(f"Response Text   : {reminder.response_text or '-'}")
            print(f"Sent At         : {reminder.sent_at.isoformat() if reminder.sent_at else '-'}")
            print(f"Responded At    : {reminder.responded_at.isoformat() if reminder.responded_at else '-'}")
            print(f"Outbound SID    : {reminder.outbound_message_id or '-'}")
            print(f"Inbound SID     : {reminder.inbound_message_id or '-'}")

        print("=" * 80)
        print(f"Total shown: {len(reminders)}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
