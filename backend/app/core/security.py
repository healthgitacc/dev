"""
Security utilities for password hashing and JWT token management.
Uses argon2 for password hashing and PyJWT for token generation/validation.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing context using argon2 (more reliable than bcrypt on Windows)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


class PasswordManager:
    """Handle password hashing and verification."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using argon2.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password from database
            
        Returns:
            True if passwords match, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)


class TokenManager:
    """Handle JWT token generation and validation."""
    
    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Dictionary of claims to encode (e.g., {"sub": user_id})
            expires_delta: Custom expiration time. If None, uses settings default.
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> dict[str, Any]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            JWTError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            raise
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[int]:
        """
        Extract user ID from token.
        
        Args:
            token: JWT token string
            
        Returns:
            User ID if valid, None otherwise
        """
        try:
            payload = TokenManager.decode_token(token)
            user_id_str: str = payload.get("sub")
            # Convert from string back to integer
            return int(user_id_str) if user_id_str else None
        except (JWTError, ValueError, TypeError):
            return None
    
    @staticmethod
    def is_token_expired(token: str) -> bool:
        """
        Check if token is expired.
        
        Args:
            token: JWT token string
            
        Returns:
            True if expired, False otherwise
        """
        try:
            TokenManager.decode_token(token)
            return False
        except JWTError:
            return True
