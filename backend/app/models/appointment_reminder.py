"""
Appointment reminder model for outbound reminder SMS and patient replies.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base


class AppointmentReminder(Base):
    """
    Tracks the latest reminder SMS sent for an appointment and the patient's reply.
    """
    __tablename__ = "appointment_reminders"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    phone_number = Column(String(32), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="pending")
    outbound_message_id = Column(String(128), nullable=True, index=True)
    inbound_message_id = Column(String(128), nullable=True, index=True)
    response_text = Column(String(255), nullable=True)
    sent_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("appointment_id", name="uq_appointment_reminder_appointment_id"),
        Index("idx_appointment_reminders_hospital_status", "hospital_id", "status"),
    )

    appointment = relationship("Appointment", back_populates="reminder", uselist=False)
    patient = relationship("Patient")

    def __repr__(self) -> str:
        return f"<AppointmentReminder appointment_id={self.appointment_id} status={self.status}>"
