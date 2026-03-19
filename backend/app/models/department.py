"""
Department model - Departments under a hospital (e.g. Ortho, Neuro, Uro).
Department admins are scoped to one department.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base


class Department(Base):
    """
    Department belongs to a hospital. Doctors can be assigned to a department.
    Department admins see only data for their department.
    """
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("hospital_id", "name", name="uq_hospital_department_name"),
        Index("idx_departments_hospital_id", "hospital_id"),
    )

    hospital = relationship("Hospital", back_populates="departments")
    doctors = relationship("Doctor", back_populates="department")
    department_admins = relationship("User", back_populates="department", foreign_keys="User.department_id")

    def __repr__(self) -> str:
        return f"<Department {self.id}: {self.name} (hospital_id={self.hospital_id})>"
