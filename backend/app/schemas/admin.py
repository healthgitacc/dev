"""
Admin-specific schemas for doctor management.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional


class CreateDoctorRequest(BaseModel):
    """Request schema for creating a new doctor."""
    name: str = Field(..., min_length=2, max_length=100, description="Doctor's professional name")
    email: str = Field(..., description="Doctor's email address")
    phone: str = Field(..., min_length=10, max_length=15, description="Doctor's phone number")
    specialization: str = Field(..., min_length=2, max_length=100, description="Medical specialization")
    experience_years: int = Field(..., ge=0, le=50, description="Years of experience")
    license_number: str = Field(..., min_length=3, max_length=50, description="Medical license number")
    department_id: int = Field(..., ge=1, description="Department ID for the doctor")
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError('Invalid email format')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        # Remove spaces and check if it contains only digits and optional + at start
        clean_phone = v.replace(' ', '')
        if not (clean_phone.isdigit() or (clean_phone.startswith('+') and clean_phone[1:].isdigit())):
            raise ValueError('Invalid phone number format')
        return v


class UpdateDoctorRequest(BaseModel):
    """Request schema for updating doctor profile."""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Doctor's professional name")
    specialization: Optional[str] = Field(None, min_length=2, max_length=100, description="Medical specialization")
    experience_years: Optional[int] = Field(None, ge=0, le=50, description="Years of experience")
    license_number: Optional[str] = Field(None, min_length=3, max_length=50, description="Medical license number")