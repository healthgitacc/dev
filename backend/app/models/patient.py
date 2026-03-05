"""
Patient model - Extends User model with health information.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
import enum


from app.database import Base


class Gender(str, enum.Enum):
    """Gender enumeration."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BloodGroup(str, enum.Enum):
    """Blood group enumeration."""
    O_PLUS = "O+"
    O_MINUS = "O-"
    A_PLUS = "A+"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B_MINUS = "B-"
    AB_PLUS = "AB+"
    AB_MINUS = "AB-"


class Patient(Base):
    """
    Patient model.
    
    Relationships:
    - Many Patients to One User
    - One Patient has many Appointments
    - One Patient has many Medical Records
    """
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    blood_group = Column(String(5), nullable=True)
    medical_history = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")

    # Indexes for common queries
    __table_args__ = (
        Index("idx_patients_user_id", "user_id"),
        Index("idx_patients_gender", "gender"),
    )

    def __repr__(self) -> str:
        return f"<Patient {self.id}: {self.user_id}>"
