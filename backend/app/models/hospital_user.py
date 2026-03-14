"""
HospitalUser association model - Links users to hospitals (Super Owner only).
Keeps hospitals table separate from the core interconnected tables
(users, doctors, patients, appointments, medical_records).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base


class HospitalUser(Base):
    """
    Association table: which users are assigned to which hospital.
    Used only by super_owner to assign hospital_admin users to hospitals.
    Core tables (users, doctors, patients, appointments, medical_records)
    remain interconnected; hospitals is separate and linked only via this table.
    """
    __tablename__ = "hospital_users"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (UniqueConstraint("hospital_id", "user_id", name="uq_hospital_user"),)

    # Relationships
    hospital = relationship("Hospital", back_populates="hospital_users")
    user = relationship("User", back_populates="hospital_assignments")

    def __repr__(self) -> str:
        return f"<HospitalUser hospital_id={self.hospital_id} user_id={self.user_id}>"
