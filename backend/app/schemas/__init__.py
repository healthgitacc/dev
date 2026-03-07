"""Schemas - Pydantic request/response validation."""
from app.schemas.base import TimestampSchema, PaginationParams, MessageResponse, ErrorResponse
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    ChangePasswordRequest,
    StaffRegisterRequest,
    PatientRegisterByStaffRequest,
    DoctorRegisterByAdminRequest,
    AppointmentCreateByStaffRequest,
    AppointmentCreateByStaffManualRequest,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    DoctorProfile,
    PatientProfile,
    UserDetailResponse,
)
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentDetailResponse,
    AppointmentListResponse,
)
from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordResponse,
    MedicalRecordDetailResponse,
    MedicalRecordListResponse,
)

__all__ = [
    # Base
    "TimestampSchema",
    "PaginationParams",
    "MessageResponse",
    "ErrorResponse",
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "ChangePasswordRequest",
    "StaffRegisterRequest",
    "PatientRegisterByStaffRequest",
    "DoctorRegisterByAdminRequest",
    "AppointmentCreateByStaffRequest",
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "DoctorProfile",
    "PatientProfile",
    "UserDetailResponse",
    # Appointment
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentResponse",
    "AppointmentDetailResponse",
    "AppointmentListResponse",
    # Medical Record
    "MedicalRecordCreate",
    "MedicalRecordUpdate",
    "MedicalRecordResponse",
    "MedicalRecordDetailResponse",
    "MedicalRecordListResponse",
]
