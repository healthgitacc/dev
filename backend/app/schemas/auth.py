"""
Authentication request/response schemas.
Handles user registration, login, and token responses.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole


class RegisterRequest(BaseModel):
    """User registration request."""
    name: str = Field(..., min_length=2, max_length=255, description="User full name")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password (min 8 characters)")
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")
    role: UserRole = Field(default=UserRole.PATIENT, description="User role")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "SecurePass123",
                "phone": "+1234567890",
                "role": "patient"
            }
        }


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "SecurePass123"
            }
        }


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user_id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    role: UserRole = Field(..., description="User role")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_id": 1,
                "email": "john@example.com",
                "role": "patient"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Change password request."""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")

    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "OldPass123",
                "new_password": "NewPass123",
                "confirm_password": "NewPass123"
            }
        }

class StaffRegisterRequest(BaseModel):
    """Hospital staff registration request (Admin only)."""
    name: str = Field(..., min_length=2, max_length=255, description="Staff full name")
    email: EmailStr = Field(..., description="Staff email address")
    password: str = Field(..., min_length=8, max_length=100, description="Staff password")
    phone: Optional[str] = Field(None, max_length=20, description="Staff phone number")
    department: Optional[str] = Field(None, max_length=100, description="Department (e.g., Front Desk, Registration)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Smith",
                "email": "staff@hospital.com",
                "password": "StaffPass123",
                "phone": "+1234567890",
                "department": "Front Desk"
            }
        }


class PatientRegisterByStaffRequest(BaseModel):
    """Patient registration request from hospital staff."""
    name: str = Field(..., min_length=2, max_length=255, description="Patient full name")
    email: EmailStr = Field(..., description="Patient email address")
    phone: str = Field(..., max_length=20, description="Patient phone number")
    blood_group: Optional[str] = Field(None, max_length=5, description="Blood group (e.g., O+, A-)")
    gender: Optional[str] = Field(None, description="Gender (M/F/Other)")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    address: Optional[str] = Field(None, max_length=500, description="Patient address")
    medical_history: Optional[str] = Field(None, max_length=1000, description="Medical history notes")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "phone": "+1234567890",
                "blood_group": "O+",
                "gender": "F",
                "date_of_birth": "1990-01-15",
                "address": "123 Main St, City, State",
                "medical_history": "Allergic to Penicillin"
            }
        }


class AppointmentCreateByStaffRequest(BaseModel):
    """Appointment creation by hospital staff on behalf of patient."""
    patient_id: int = Field(..., gt=0, description="Patient ID")
    doctor_id: int = Field(..., gt=0, description="Doctor ID")
    appointment_date: str = Field(..., description="Appointment date and time (ISO format)")
    duration_minutes: int = Field(30, ge=15, le=120, description="Appointment duration in minutes")
    chief_complaint: str = Field(..., min_length=5, max_length=500, description="Chief complaint / reason for visit")
    symptoms: Optional[str] = Field(None, max_length=500, description="Patient symptoms")
    notes: Optional[str] = Field(None, max_length=500, description="Additional appointment notes")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 1,
                "doctor_id": 1,
                "appointment_date": "2026-03-01T14:00:00Z",
                "duration_minutes": 30,
                "chief_complaint": "Chest pain and shortness of breath",
                "symptoms": "Pain for 2 days, difficulty breathing",
                "notes": "Patient walks with difficulty"
            }
        }


class AppointmentCreateByStaffManualRequest(BaseModel):
    """Appointment creation with manual patient information."""
    patient_name: str = Field(..., min_length=1, max_length=100, description="Patient full name")
    patient_email: str = Field(..., description="Patient email (unique identifier)")
    patient_phone: str = Field(..., min_length=10, max_length=20, description="Patient phone number")
    doctor_id: int = Field(..., gt=0, description="Doctor ID")
    appointment_date: str = Field(..., description="Appointment date and time (ISO format with Z)")
    duration_minutes: int = Field(30, ge=15, le=120, description="Appointment duration in minutes")
    chief_complaint: str = Field(..., min_length=5, max_length=500, description="Chief complaint / reason for visit")
    symptoms: Optional[str] = Field(None, max_length=500, description="Patient symptoms")
    notes: Optional[str] = Field(None, max_length=500, description="Additional appointment notes")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_name": "John Doe",
                "patient_email": "john@example.com",
                "patient_phone": "+1-234-567-8900",
                "doctor_id": 1,
                "appointment_date": "2026-03-01T14:00:00Z",
                "duration_minutes": 30,
                "chief_complaint": "Chest pain and shortness of breath",
                "symptoms": "Pain for 2 days, difficulty breathing",
                "notes": "Patient walks with difficulty"
            }
        }