"""
User model with role-based access control.
Base model for all user types (Admin, Doctor, Patient).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    SUPER_ADMIN = "super_admin"
    SUPER_OWNER = "super_owner"
    HOSPITAL_ADMIN = "hospital_admin"
    DEPARTMENT_ADMIN = "department_admin"
    DOCTOR = "doctor"
    PATIENT = "patient"


class User(Base):
    """
    User model - Base class for all user types.
    
    Relationships:
    - One User can have one Doctor profile
    - One User can have one Patient profile
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.PATIENT.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships (users, doctors, patients, appointments, medical_records are interconnected;
    # hospitals is separate and only linked via hospital_assignments for super_owner)
    doctor = relationship("Doctor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    patient = relationship("Patient", back_populates="user", uselist=False, cascade="all, delete-orphan")
    hospital_assignments = relationship("HospitalUser", back_populates="user", cascade="all, delete-orphan")
    department = relationship("Department", back_populates="department_admins", foreign_keys=[department_id])
    created_by = relationship("User", remote_side="User.id", foreign_keys=[created_by_id])

    # Indexes for common queries
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_role", "role"),
        Index("idx_users_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<User {self.id}: {self.email} ({self.role})>"
