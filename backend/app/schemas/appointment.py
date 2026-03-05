"""
Appointment request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    """Appointment creation request."""
    doctor_id: int = Field(..., description="Doctor ID")
    appointment_date: datetime = Field(..., description="Appointment date and time")
    duration_minutes: int = Field(default=30, ge=15, le=120, description="Appointment duration in minutes")
    notes: Optional[str] = Field(None, max_length=500, description="Appointment notes")

    class Config:
        json_schema_extra = {
            "example": {
                "doctor_id": 1,
                "appointment_date": "2026-03-15T14:30:00",
                "duration_minutes": 30,
                "notes": "Routine checkup"
            }
        }


class AppointmentUpdate(BaseModel):
    """Appointment update request."""
    appointment_date: Optional[datetime] = Field(None, description="New appointment date and time")
    duration_minutes: Optional[int] = Field(None, ge=15, le=120, description="Appointment duration in minutes")
    notes: Optional[str] = Field(None, max_length=500, description="Appointment notes")
    status: Optional[AppointmentStatus] = Field(None, description="Appointment status")


class AppointmentResponse(BaseModel):
    """Appointment response schema."""
    id: int = Field(..., description="Appointment ID")
    doctor_id: int = Field(..., description="Doctor ID")
    patient_id: int = Field(..., description="Patient ID")
    appointment_date: datetime = Field(..., description="Appointment date and time")
    duration_minutes: int = Field(..., description="Appointment duration in minutes")
    status: AppointmentStatus = Field(..., description="Appointment status")
    notes: Optional[str] = Field(None, description="Appointment notes")
    reminder_sent: Optional[datetime] = Field(None, description="Reminder sent timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class AppointmentDetailResponse(AppointmentResponse):
    """Detailed appointment response with doctor and patient info."""
    doctor_name: str = Field(..., description="Doctor name")
    doctor_specialization: str = Field(..., description="Doctor specialization")
    patient_name: str = Field(..., description="Patient name")
    patient_email: str = Field(..., description="Patient email")


class AppointmentListResponse(BaseModel):
    """Appointment list response with pagination."""
    total: int = Field(..., description="Total number of appointments")
    skip: int = Field(..., description="Records skipped")
    limit: int = Field(..., description="Records limit")
    items: list[AppointmentResponse] = Field(..., description="List of appointments")
