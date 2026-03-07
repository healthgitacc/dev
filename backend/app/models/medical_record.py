"""
Medical Record model - Stores patient medical records, diagnoses, and prescriptions.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Text, Index
from sqlalchemy.orm import relationship

from app.database import Base


class MedicalRecord(Base):
    """
    Medical Record model.
    
    Relationships:
    - Many Medical Records to One Patient
    - Many Medical Records to One Doctor (who created the record)
    """
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Medical information
    disease_name = Column(String(255), nullable=False)
    diagnosis = Column(Text, nullable=False)
    prescription_text = Column(Text, nullable=True)
    dosage = Column(String(255), nullable=True)
    
    # Follow-up and metadata
    follow_up_date = Column(DateTime, nullable=True, index=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")

    # Indexes for common queries
    __table_args__ = (
        Index("idx_medical_records_patient_id", "patient_id"),
        Index("idx_medical_records_doctor_id", "doctor_id"),
        Index("idx_medical_records_created_at", "created_at"),
        Index("idx_medical_records_follow_up_date", "follow_up_date"),
    )

    def __repr__(self) -> str:
        return f"<MedicalRecord {self.id}: {self.disease_name}>"
