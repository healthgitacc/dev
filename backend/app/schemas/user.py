"""
User request/response schemas.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    name: str = Field(..., min_length=2, max_length=255, description="User full name")
    email: EmailStr = Field(..., description="User email address")
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")
    role: UserRole = Field(..., description="User role")


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8, max_length=100, description="User password")


class UserUpdate(BaseModel):
    """User update schema."""
    name: Optional[str] = Field(None, min_length=2, max_length=255, description="User full name")
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")


class UserResponse(UserBase):
    """User response schema."""
    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="User active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class DoctorProfile(BaseModel):
    """Doctor profile information."""
    id: int = Field(..., description="Doctor ID")
    specialization: str = Field(..., description="Medical specialization")
    experience_years: int = Field(..., description="Years of experience")
    license_number: Optional[str] = Field(None, description="Medical license number")

    class Config:
        from_attributes = True


class PatientProfile(BaseModel):
    """Patient profile information."""
    id: int = Field(..., description="Patient ID")
    age: Optional[int] = Field(None, description="Patient age")
    gender: Optional[str] = Field(None, description="Patient gender")
    blood_group: Optional[str] = Field(None, description="Patient blood group")
    medical_history: Optional[str] = Field(None, description="Patient medical history")

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Detailed user response with role-specific profile."""
    doctor: Optional[DoctorProfile] = Field(None, description="Doctor profile if user is doctor")
    patient: Optional[PatientProfile] = Field(None, description="Patient profile if user is patient")
