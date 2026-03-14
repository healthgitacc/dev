"""
Appointment model - Represents scheduled appointments between doctors and patients.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Text, Index
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class AppointmentStatus(str, enum.Enum):
    """Appointment status enumeration."""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class Appointment(Base):
    """
    Appointment model.
    
    Relationships:
    - Many Appointments to One Doctor
    - Many Appointments to One Patient
    """
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    appointment_date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=30, nullable=False)
    status = Column(String(50), default=AppointmentStatus.SCHEDULED.value, nullable=False)
    notes = Column(Text, nullable=True)
    reminder_sent = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    doctor = relationship("Doctor", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")

    # Indexes for common queries
    __table_args__ = (
        Index("idx_appointments_doctor_id", "doctor_id"),
        Index("idx_appointments_patient_id", "patient_id"),
        Index("idx_appointments_date", "appointment_date"),
        Index("idx_appointments_status", "status"),
        Index("idx_appointments_doctor_date", "doctor_id", "appointment_date"),
    )

    def __repr__(self) -> str:
        return f"<Appointment {self.id}: {self.appointment_date} ({self.status})>"
