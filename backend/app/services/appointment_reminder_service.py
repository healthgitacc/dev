"""
Appointment reminder service for hospital-admin reminder workflows.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core import AuthorizationError, ValidationError, get_logger
from app.models import Appointment, AppointmentReminder, AppointmentStatus, Doctor, Hospital, HospitalUser, Patient, User
from app.services.notification_service import NotificationService

logger = get_logger(__name__)


class AppointmentReminderService:
    """Manage reminder listing, sending, and reply processing."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _normalize_phone(phone_number: Optional[str]) -> str:
        if not phone_number:
            return ""
        digits = "".join(ch for ch in phone_number if ch.isdigit())
        return digits[-10:] if len(digits) >= 10 else digits

    def _mark_expired_no_responses(self, hospital_id: int) -> None:
        now = datetime.now(timezone.utc)
        reminders = (
            self.db.query(AppointmentReminder)
            .join(Appointment, Appointment.id == AppointmentReminder.appointment_id)
            .filter(
                AppointmentReminder.hospital_id == hospital_id,
                AppointmentReminder.status == "sent",
                Appointment.appointment_date < now,
            )
            .all()
        )
        changed = False
        for reminder in reminders:
            reminder.status = "no_response"
            changed = True
        if changed:
            self.db.commit()

    def list_upcoming_reminders(
        self,
        hospital_id: int,
        skip: int = 0,
        limit: int = 100,
        days_ahead: int = 7,
        status: Optional[str] = None,
    ) -> tuple[list[dict], int]:
        self._mark_expired_no_responses(hospital_id)

        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(days=days_ahead)

        appointments = (
            self.db.query(Appointment)
            .join(Doctor, Doctor.id == Appointment.doctor_id)
            .join(User, User.id == Doctor.user_id)
            .join(HospitalUser, HospitalUser.user_id == User.id)
            .filter(
                HospitalUser.hospital_id == hospital_id,
                Appointment.appointment_date >= now,
                Appointment.appointment_date <= cutoff,
                Appointment.status.in_([AppointmentStatus.SCHEDULED.value, AppointmentStatus.RESCHEDULED.value]),
            )
            .order_by(Appointment.appointment_date.asc())
            .all()
        )

        items: list[dict] = []
        for appointment in appointments:
            reminder = (
                self.db.query(AppointmentReminder)
                .filter(AppointmentReminder.appointment_id == appointment.id)
                .first()
            )
            effective_status = reminder.status if reminder else "pending"
            if status and effective_status != status:
                continue

            hospital = (
                self.db.query(Hospital)
                .filter(Hospital.id == hospital_id)
                .first()
            )
            patient_phone = appointment.patient.user.phone if appointment.patient and appointment.patient.user else None
            items.append(
                {
                    "appointment_id": appointment.id,
                    "patient_id": appointment.patient_id,
                    "patient_name": appointment.patient.user.name if appointment.patient and appointment.patient.user else "Patient",
                    "patient_phone": patient_phone,
                    "doctor_id": appointment.doctor_id,
                    "doctor_name": appointment.doctor.name if appointment.doctor else "Doctor",
                    "hospital_name": hospital.name if hospital else None,
                    "appointment_date": appointment.appointment_date.isoformat(),
                    "appointment_status": appointment.status,
                    "reminder_status": effective_status,
                    "message_id": reminder.outbound_message_id if reminder else None,
                    "sent_at": reminder.sent_at.isoformat() if reminder and reminder.sent_at else None,
                    "responded_at": reminder.responded_at.isoformat() if reminder and reminder.responded_at else None,
                    "response_text": reminder.response_text if reminder else None,
                }
            )

        total = len(items)
        return items[skip: skip + limit], total

    def send_reminders(self, hospital_id: int, appointment_ids: list[int]) -> dict:
        if not appointment_ids:
            raise ValidationError("Select at least one appointment", field="appointment_ids")

        hospital = self.db.query(Hospital).filter(Hospital.id == hospital_id).first()
        if not hospital:
            raise ValidationError("Hospital not found", field="hospital_id")

        notification_service = NotificationService()
        sent = 0
        failed = 0
        items: list[dict] = []

        appointments = (
            self.db.query(Appointment)
            .join(Doctor, Doctor.id == Appointment.doctor_id)
            .join(User, User.id == Doctor.user_id)
            .join(HospitalUser, HospitalUser.user_id == User.id)
            .filter(
                Appointment.id.in_(appointment_ids),
                HospitalUser.hospital_id == hospital_id,
                Appointment.status.in_([AppointmentStatus.SCHEDULED.value, AppointmentStatus.RESCHEDULED.value]),
            )
            .all()
        )
        found_ids = {appointment.id for appointment in appointments}
        missing_ids = sorted(set(appointment_ids) - found_ids)
        if missing_ids:
            raise AuthorizationError("One or more selected appointments do not belong to your hospital")

        for appointment in appointments:
            patient_user = appointment.patient.user if appointment.patient else None
            phone_number = patient_user.phone if patient_user else None
            if not phone_number:
                failed += 1
                items.append({"appointment_id": appointment.id, "success": False, "error": "Patient phone number is missing"})
                continue

            result = notification_service.send_patient_response_reminder(
                phone_number=phone_number,
                patient_name=patient_user.name,
                doctor_name=appointment.doctor.name if appointment.doctor else "Doctor",
                hospital_name=hospital.name,
                appointment_datetime=appointment.appointment_date,
            )

            reminder = self.db.query(AppointmentReminder).filter(AppointmentReminder.appointment_id == appointment.id).first()
            if not reminder:
                reminder = AppointmentReminder(
                    appointment_id=appointment.id,
                    hospital_id=hospital_id,
                    patient_id=appointment.patient_id,
                    phone_number=self._normalize_phone(phone_number),
                )
                self.db.add(reminder)

            reminder.phone_number = self._normalize_phone(phone_number)
            reminder.outbound_message_id = result.get("message_id")
            reminder.sent_at = datetime.utcnow()
            reminder.responded_at = None
            reminder.inbound_message_id = None
            reminder.response_text = None
            reminder.status = "sent" if result.get("success") else "failed"
            appointment.reminder_sent = datetime.utcnow() if result.get("success") else appointment.reminder_sent

            if result.get("success"):
                sent += 1
            else:
                failed += 1

            items.append(
                {
                    "appointment_id": appointment.id,
                    "success": result.get("success", False),
                    "message_id": result.get("message_id"),
                    "error": result.get("error"),
                }
            )

        self.db.commit()
        return {"sent": sent, "failed": failed, "items": items}

    def record_reply(self, from_phone: str, body: str, inbound_message_id: Optional[str] = None) -> Optional[AppointmentReminder]:
        normalized_phone = self._normalize_phone(from_phone)
        if not normalized_phone:
            return None

        normalized_body = (body or "").strip().lower()
        if normalized_body.startswith("yes"):
            new_status = "yes"
        elif normalized_body.startswith("no"):
            new_status = "no"
        else:
            return None

        reminder = (
            self.db.query(AppointmentReminder)
            .join(Appointment, Appointment.id == AppointmentReminder.appointment_id)
            .filter(
                AppointmentReminder.phone_number == normalized_phone,
                AppointmentReminder.status.in_(["sent", "no_response", "pending"]),
            )
            .order_by(AppointmentReminder.sent_at.desc().nullslast(), Appointment.appointment_date.asc())
            .first()
        )
        if not reminder:
            return None

        reminder.status = new_status
        reminder.response_text = body
        reminder.responded_at = datetime.utcnow()
        reminder.inbound_message_id = inbound_message_id
        self.db.commit()
        self.db.refresh(reminder)
        return reminder
