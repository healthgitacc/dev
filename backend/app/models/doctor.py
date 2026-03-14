"""
Doctor model - Extends User model with medical specialization details.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship

from app.models.base import Base


class Doctor(Base):
    """
    Doctor model.
    
    Relationships:
    - Many Doctors to One User
    - One Doctor has many Appointments
    - One Doctor has many Medical Records
    
    Note: 'name' is stored here (doctor's professional name), separate from user's authentication info
    """
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    specialization = Column(String(255), nullable=False)
    experience_years = Column(Integer, nullable=False, default=0)
    license_number = Column(String(100), nullable=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
    medical_records = relationship("MedicalRecord", back_populates="doctor", cascade="all, delete-orphan")

    # Indexes for common queries
    __table_args__ = (
        Index("idx_doctors_user_id", "user_id"),
        Index("idx_doctors_name", "name"),
        Index("idx_doctors_specialization", "specialization"),
        Index("idx_doctors_license_number", "license_number"),
    )

    def __repr__(self) -> str:
        return f"<Doctor {self.id}: {self.name} ({self.specialization})>"
