#!/usr/bin/env python3
"""
Create the appointment_reminders table if it does not exist.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_migration():
    from app.core.engine import engine
    from app.models.appointment_reminder import AppointmentReminder

    AppointmentReminder.__table__.create(bind=engine, checkfirst=True)
    print("appointment_reminders table is ready.")


if __name__ == "__main__":
    run_migration()
