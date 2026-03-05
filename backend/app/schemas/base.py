"""
Base Pydantic schemas used across the application.
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class TimestampSchema(BaseModel):
    """Base schema with created_at and updated_at timestamps."""
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(10, ge=1, le=100, description="Number of records to return")


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str = Field(..., description="Response message")


class ErrorResponse(BaseModel):
    """Generic error response."""
    detail: str = Field(..., description="Error detail")
    error_code: Optional[str] = Field(None, description="Error code for handling")
