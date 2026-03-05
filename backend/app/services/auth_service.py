"""
Authentication service for user registration, login, and password management.
Implements authentication business logic.
"""
from sqlalchemy.orm import Session
from datetime import timedelta
from app.models import User, Doctor, Patient, UserRole
from app.core import (
    PasswordManager,
    TokenManager,
    InvalidCredentialsError,
    ConflictError,
    ValidationError,
    NotFoundError,
    get_logger,
    security_logger,
)
from app.schemas import RegisterRequest, LoginRequest, TokenResponse, ChangePasswordRequest


logger = get_logger(__name__)


class AuthService:
    """Handle authentication operations."""
    
    def __init__(self, db: Session):
        """
        Initialize auth service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def register_user(self, data: RegisterRequest) -> TokenResponse:
        """
        Register a new user.
        
        Args:
            data: Registration request data
            
        Returns:
            TokenResponse with JWT token and user info
            
        Raises:
            ConflictError: If email already exists
            ValidationError: If validation fails
        """
        # Check if email already exists
        existing_user = self.db.query(User).filter(User.email == data.email).first()
        if existing_user:
            security_logger.warning(f"Registration attempt with existing email: {data.email}")
            raise ConflictError(f"Email {data.email} already registered", field="email")
        
        # Validate password strength
        self._validate_password_strength(data.password)
        
        # Hash password
        password_hash = PasswordManager.hash_password(data.password)
        
        try:
            # Create user
            user = User(
                name=data.name,
                email=data.email,
                phone=data.phone,
                password_hash=password_hash,
                role=data.role if isinstance(data.role, str) else data.role.value,
                is_active=True,
            )
            
            self.db.add(user)
            self.db.flush()  # Get user.id without committing
            
            # Create role-specific profile
            if data.role == UserRole.DOCTOR:
                doctor = Doctor(user_id=user.id, specialization="", experience_years=0)
                self.db.add(doctor)
            elif data.role == UserRole.PATIENT:
                patient = Patient(user_id=user.id)
                self.db.add(patient)
            
            self.db.commit()
            self.db.refresh(user)
            
            security_logger.info(f"User registered: {user.email} as {user.role}")
            
            # Generate token
            return self._create_token_response(user)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Registration error: {str(e)}")
            raise
    
    def login(self, data: LoginRequest) -> TokenResponse:
        """
        Authenticate user and return JWT token.
        
        Args:
            data: Login credentials
            
        Returns:
            TokenResponse with JWT token
            
        Raises:
            InvalidCredentialsError: If email or password is incorrect
        """
        # Find user by email
        user = self.db.query(User).filter(User.email == data.email).first()
        
        if not user:
            security_logger.warning(f"Login attempt with non-existent email: {data.email}")
            raise InvalidCredentialsError()
        
        # Verify password
        if not PasswordManager.verify_password(data.password, user.password_hash):
            security_logger.warning(f"Failed login attempt for: {data.email}")
            raise InvalidCredentialsError()
        
        if not user.is_active:
            security_logger.warning(f"Login attempt with inactive account: {data.email}")
            raise ValidationError("User account is not active", field="email")
        
        security_logger.info(f"User logged in: {user.email}")
        
        return self._create_token_response(user)
    
    def change_password(self, user_id: int, data: ChangePasswordRequest) -> dict:
        """
        Change user password.
        
        Args:
            user_id: User ID
            data: Password change request
            
        Returns:
            Success message
            
        Raises:
            NotFoundError: If user not found
            InvalidCredentialsError: If old password is incorrect
            ValidationError: If new passwords don't match or password is weak
        """
        # Find user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User", user_id)
        
        # Verify old password
        if not PasswordManager.verify_password(data.old_password, user.password_hash):
            security_logger.warning(f"Failed password change attempt for user {user_id}")
            raise InvalidCredentialsError()
        
        # Validate new password
        if data.new_password != data.confirm_password:
            raise ValidationError("New passwords do not match", field="new_password")
        
        self._validate_password_strength(data.new_password)
        
        # Check if new password is same as old
        if PasswordManager.verify_password(data.new_password, user.password_hash):
            raise ValidationError("New password must be different from old password", field="new_password")
        
        # Update password
        try:
            user.password_hash = PasswordManager.hash_password(data.new_password)
            self.db.commit()
            
            security_logger.info(f"Password changed for user {user_id}")
            
            return {"message": "Password changed successfully"}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error changing password: {str(e)}")
            raise
    
    def _create_token_response(self, user: User) -> TokenResponse:
        """
        Create JWT token response for user.
        
        Args:
            user: User object
            
        Returns:
            TokenResponse
        """
        # Convert user.id to string for JWT 'sub' claim (must be string per JWT spec)
        access_token = TokenManager.create_access_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            role=user.role,
        )
    
    @staticmethod
    def _validate_password_strength(password: str) -> None:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Raises:
            ValidationError: If password doesn't meet requirements
        """
        errors = []
        
        # Check length
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        
        # Check for uppercase
        if not any(c.isupper() for c in password):
            errors.append("Password must contain uppercase letter")
        
        # Check for lowercase
        if not any(c.islower() for c in password):
            errors.append("Password must contain lowercase letter")
        
        # Check for digit
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain digit")
        
        # Check for special character
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            errors.append("Password must contain special character")
        
        if errors:
            raise ValidationError("; ".join(errors), field="password")
