"""
Authentication routes.
Handles user registration, login, and password management.
"""
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import AuthService
from app.core import get_current_user, AppException, app_exception_to_http, get_logger
from app.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    ChangePasswordRequest,
    MessageResponse,
)
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger(__name__)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "Email already exists"},
        422: {"description": "Validation error"},
    },
)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Register a new user account.
    
    Creates a new user with the specified role (admin/doctor/patient).
    Returns JWT token immediately upon successful registration.
    
    Args:
        request: Registration request with user details
        db: Database session
        
    Returns:
        TokenResponse with JWT token and user info
        
    Raises:
        409 Conflict: Email already exists
        422 Unprocessable Entity: Invalid password strength
    """
    try:
        auth_service = AuthService(db)
        token_response = auth_service.register_user(request)
        logger.info(f"User registered: {request.email}")
        return token_response
    except AppException as exc:
        logger.error(f"AppException during registration: {exc.code} - {exc.message}")
        raise app_exception_to_http(exc)
    except Exception as exc:
        import traceback
        logger.error(f"Registration error: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)  # Include actual error in response for debugging
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"description": "Invalid credentials"},
        422: {"description": "User account inactive"},
    },
)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    User login with email and password.
    
    Authenticates user and returns JWT token for subsequent requests.
    
    Args:
        request: Login credentials (email and password)
        db: Database session
        
    Returns:
        TokenResponse with JWT token and user info
        
    Raises:
        401 Unauthorized: Invalid email or password
        422 Unprocessable Entity: Account not active
    """
    try:
        auth_service = AuthService(db)
        token_response = auth_service.login(request)
        logger.info(f"User logged in: {request.email}")
        return token_response
    except AppException as exc:
        raise app_exception_to_http(exc)
    except Exception as exc:
        logger.error(f"Login error: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    responses={
        401: {"description": "Old password incorrect"},
        400: {"description": "Password validation failed"},
    },
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """
    Change user password (requires authentication).
    
    Updates user password with validation of old password and strength requirements.
    
    Args:
        request: Password change request with old and new passwords
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        401 Unauthorized: Old password incorrect
        400 Bad Request: Password validation failed
        404 Not Found: User not found
    """
    try:
        auth_service = AuthService(db)
        result = auth_service.change_password(current_user.id, request)
        logger.info(f"Password changed for user: {current_user.email}")
        return result
    except AppException as exc:
        raise app_exception_to_http(exc)
    except Exception as exc:
        logger.error(f"Change password error: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/me",
    response_model=dict,
    responses={
        401: {"description": "Unauthorized"},
    },
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get current authenticated user information.
    
    Returns information about the currently authenticated user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information (id, email, name, role, etc.)
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "phone": current_user.phone,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }
