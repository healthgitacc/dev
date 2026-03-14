"""Core module - Security, configuration, and utilities."""
from app.core.config import settings, Settings
from app.core.security import PasswordManager, TokenManager, pwd_context
from app.core.exceptions import (
    AppException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    InvalidTokenError,
    InvalidCredentialsError,
    UserNotActiveError,
    AppointmentConflictError,
    InvalidAppointmentStatusError,
    BusinessLogicError,
    app_exception_to_http,
)
from app.core.logger import get_logger, logger, audit_logger, db_logger, security_logger
from app.core.utils import (
    PaginatedResponse,
    paginate,
    validate_pagination,
    filter_model_dict,
    format_datetime_response,
    generate_error_response,
    generate_temporary_password,
)

__all__ = [
    # Config
    "settings",
    "Settings",
    # Security
    "PasswordManager",
    "TokenManager",
    "pwd_context",
    # Exceptions
    "AppException",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "InvalidTokenError",
    "InvalidCredentialsError",
    "UserNotActiveError",
    "AppointmentConflictError",
    "InvalidAppointmentStatusError",
    "BusinessLogicError",
    "app_exception_to_http",
# Logger
    "get_logger",
    "logger",
    "audit_logger",
    "db_logger",
    "security_logger",
]

# Auth dependencies - moved to bottom to avoid circular imports
from app.core.auth import (
    get_current_user,
    get_optional_user,
    get_current_admin,
    get_current_doctor,
    get_current_patient,
    get_current_doctor_or_patient,
    get_current_staff_or_admin,
    get_current_super_admin,
    get_current_super_owner,
    get_current_hospital_admin_or_super_owner,
    security,
)

__all__.extend([
    # Auth dependencies
    "get_current_user",
    "get_optional_user",
    "get_current_admin",
    "get_current_doctor",
    "get_current_patient",
    "get_current_doctor_or_patient",
    "get_current_staff_or_admin",
    "get_current_super_admin",
    "get_current_super_owner",
    "get_current_hospital_admin_or_super_owner",
    "security",
])
