"""
Medical Record request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MedicalRecordCreate(BaseModel):
    """Medical record creation request."""
    disease_name: str = Field(..., min_length=3, max_length=255, description="Disease name")
    diagnosis: str = Field(..., min_length=10, description="Medical diagnosis")
    prescription_text: Optional[str] = Field(None, description="Prescription text")
    dosage: Optional[str] = Field(None, max_length=255, description="Medication dosage")
    follow_up_date: Optional[datetime] = Field(None, description="Follow-up appointment date")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "disease_name": "Type 2 Diabetes",
                "diagnosis": "Patient presents with elevated blood sugar levels, consistent with Type 2 Diabetes",
                "prescription_text": "Metformin 500mg",
                "dosage": "Once daily after meals",
                "follow_up_date": "2026-04-15T10:00:00",
                "notes": "Patient to monitor blood sugar levels regularly"
            }
        }


class MedicalRecordUpdate(BaseModel):
    """Medical record update request."""
    disease_name: Optional[str] = Field(None, min_length=3, max_length=255, description="Disease name")
    diagnosis: Optional[str] = Field(None, min_length=10, description="Medical diagnosis")
    prescription_text: Optional[str] = Field(None, description="Prescription text")
    dosage: Optional[str] = Field(None, max_length=255, description="Medication dosage")
    follow_up_date: Optional[datetime] = Field(None, description="Follow-up appointment date")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


class MedicalRecordResponse(BaseModel):
    """Medical record response schema."""
    id: int = Field(..., description="Medical record ID")
    patient_id: int = Field(..., description="Patient ID")
    doctor_id: Optional[int] = Field(None, description="Doctor ID")
    disease_name: str = Field(..., description="Disease name")
    diagnosis: str = Field(..., description="Medical diagnosis")
    prescription_text: Optional[str] = Field(None, description="Prescription text")
    dosage: Optional[str] = Field(None, description="Medication dosage")
    follow_up_date: Optional[datetime] = Field(None, description="Follow-up appointment date")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class MedicalRecordDetailResponse(MedicalRecordResponse):
    """Detailed medical record response with doctor and patient info."""
    doctor_name: Optional[str] = Field(None, description="Doctor name who created the record")
    doctor_specialization: Optional[str] = Field(None, description="Doctor specialization")
    patient_name: str = Field(..., description="Patient name")


class MedicalRecordListResponse(BaseModel):
    """Medical record list response with pagination."""
    total: int = Field(..., description="Total number of records")
    skip: int = Field(..., description="Records skipped")
    limit: int = Field(..., description="Records limit")
    items: list[MedicalRecordResponse] = Field(..., description="List of medical records")
