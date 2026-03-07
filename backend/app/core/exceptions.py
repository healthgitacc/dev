"""
Custom exception classes for the application.
Provides structured error handling across the API.
"""
from fastapi import HTTPException, status
from typing import Optional, Any


class AppException(Exception):
    """Base exception for the application."""
    
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        """
        Initialize AppException.
        
        Args:
            message: Error message
            code: Error code for frontend error handling
        """
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationError(AppException):
    """Validation error exception."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        """
        Initialize ValidationError.
        
        Args:
            message: Error message
            field: Field that failed validation (optional)
        """
        self.field = field
        code = f"VALIDATION_ERROR_{field.upper()}" if field else "VALIDATION_ERROR"
        super().__init__(message, code)


class AuthenticationError(AppException):
    """Authentication failed exception."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(AppException):
    """Authorization failed exception."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "AUTHORIZATION_ERROR")


class NotFoundError(AppException):
    """Resource not found exception."""
    
    def __init__(self, resource: str, identifier: Any):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, f"{resource.upper()}_NOT_FOUND")


class ConflictError(AppException):
    """Resource conflict exception (e.g., duplicate email)."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        code = f"CONFLICT_{field.upper()}" if field else "CONFLICT"
        super().__init__(message, code)


class InvalidTokenError(AuthenticationError):
    """Invalid or expired JWT token."""
    
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message)


class InvalidCredentialsError(AuthenticationError):
    """Invalid email or password."""
    
    def __init__(self):
        super().__init__("Invalid email or password")


class UserNotActiveError(AuthorizationError):
    """User account is not active."""
    
    def __init__(self):
        super().__init__("User account is not active")


class AppointmentConflictError(ConflictError):
    """Appointment time conflict."""
    
    def __init__(self, message: str = "Appointment time slot is already booked"):
        super().__init__(message, "appointment")


class InvalidAppointmentStatusError(ValidationError):
    """Invalid appointment status transition."""
    
    def __init__(self, current_status: str, new_status: str):
        message = f"Cannot transition from {current_status} to {new_status}"
        super().__init__(message, "appointment_status")


class BusinessLogicError(AppException):
    """Business logic error exception."""
    
    def __init__(self, message: str):
        super().__init__(message, "BUSINESS_LOGIC_ERROR")


# HTTP Exception Converters
def app_exception_to_http(exc: AppException) -> HTTPException:
    """
    Convert AppException to HTTPException.
    
    Args:
        exc: AppException instance
        
    Returns:
        HTTPException with appropriate status code
    """
    status_map = {
        "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
        "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "CONFLICT": status.HTTP_409_CONFLICT,
    }
    
    # Determine status code based on exception code
    http_status = status.HTTP_400_BAD_REQUEST  # Default
    
    for key, value in status_map.items():
        if key in exc.code:
            http_status = value
            break
    
    return HTTPException(
        status_code=http_status,
        detail={"message": exc.message, "code": exc.code}
    )
