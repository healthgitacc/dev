"""
FastAPI dependency functions for authentication and authorization.
Provides reusable dependency injection for protecting routes.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional
from dataclasses import dataclass

from app.core.security import TokenManager
from app.core.exceptions import (
    InvalidTokenError,
    InvalidCredentialsError,
    AuthorizationError,
    NotFoundError,
    UserNotActiveError,
)
from app.database import get_db
from app.models import User, UserRole
from app.schemas import UserDetailResponse

# HTTP Bearer token scheme
security = HTTPBearer()


# Define HTTPAuthCredentials class for compatibility
@dataclass
class HTTPAuthCredentials:
    scheme: str
    credentials: str


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token from request
        db: Database session
        
    Returns:
        Current User object
        
    Raises:
        InvalidTokenError: If token is invalid or expired
        NotFoundError: If user not found in database
        UserNotActiveError: If user account is inactive
    """
    token = credentials.credentials
    
    # Decode and validate token
    try:
        payload = TokenManager.decode_token(token)
        user_id_str: str = payload.get("sub")
        # Convert from string back to integer
        user_id: int = int(user_id_str) if user_id_str else None
        
        if user_id is None:
            raise InvalidTokenError("Token missing user ID")
            
    except Exception:
        raise InvalidTokenError()
    
    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise NotFoundError("User", user_id)
    
    if not user.is_active:
        raise UserNotActiveError()
    
    return user


async def get_optional_user(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthCredentials] = Depends(security)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    Useful for endpoints that support both authenticated and anonymous access.
    
    Args:
        db: Database session
        credentials: HTTP Bearer token (optional)
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except Exception:
        return None


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure current user is hospital admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if hospital admin
        
    Raises:
        AuthorizationError: If user is not hospital admin
    """
    if current_user.role != UserRole.HOSPITAL_ADMIN:
        raise AuthorizationError("Hospital admin access required")
    
    return current_user


async def get_current_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure current user is super admin only.
    Super Admin: Can approve hospitals, activate/deactivate, manage all systems.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if super admin
        
    Raises:
        AuthorizationError: If user is not super admin
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise AuthorizationError("Super admin access required. Only application owner can perform this action.")
    
    return current_user


async def get_current_doctor(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure current user is doctor.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if doctor
        
    Raises:
        AuthorizationError: If user is not doctor
    """
    if current_user.role != UserRole.DOCTOR:
        raise AuthorizationError("Doctor access required")
    
    return current_user


async def get_current_patient(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure current user is patient.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if patient
        
    Raises:
        AuthorizationError: If user is not patient
    """
    if current_user.role != UserRole.PATIENT:
        raise AuthorizationError("Patient access required")
    
    return current_user


async def get_current_doctor_or_patient(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency for routes accessible by both doctors and patients.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if doctor or patient
        
    Raises:
        AuthorizationError: If user is not doctor or patient
    """
    if current_user.role not in [UserRole.DOCTOR, UserRole.PATIENT]:
        raise AuthorizationError("Doctor or Patient access required")
    
    return current_user


async def get_current_hospital_staff(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure current user is hospital admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if hospital admin
        
    Raises:
        AuthorizationError: If user is not hospital admin
    """
    if current_user.role != UserRole.HOSPITAL_ADMIN:
        raise AuthorizationError("Hospital admin access required")
    
    return current_user


async def get_current_staff_or_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency for routes accessible by super admin and hospital admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if super admin or hospital admin
        
    Raises:
        AuthorizationError: If user is not admin
    """
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN]:
        raise AuthorizationError("Admin access required")
    
    return current_user


# Exception handlers for authentication errors
def handle_invalid_token() -> HTTPException:
    """Create HTTPException for invalid token."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"message": "Invalid or expired token", "code": "INVALID_TOKEN"},
        headers={"WWW-Authenticate": "Bearer"},
    )


def handle_insufficient_permissions() -> HTTPException:
    """Create HTTPException for insufficient permissions."""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"message": "Insufficient permissions", "code": "INSUFFICIENT_PERMISSIONS"},
    )
