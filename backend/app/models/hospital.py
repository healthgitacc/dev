"""
Hospital model for Super Owner management.
Represents a hospital entity that can be managed by Super Owner.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class HospitalStatus(str, enum.Enum):
    """Hospital status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class Hospital(Base):
    """
    Hospital model - Represents a hospital managed by Super Owner.
    
    Super Owner can create, activate, deactivate, and delete hospitals.
    No patient, doctor, or appointment data is stored here.
    """
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    status = Column(SQLEnum(HospitalStatus), default=HospitalStatus.INACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Link to users only via association table (hospitals table is for super_owner only;
    # core tables users, doctors, patients, appointments, medical_records are interconnected)
    hospital_users = relationship("HospitalUser", back_populates="hospital", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Hospital {self.id}: {self.name} ({self.status})>"