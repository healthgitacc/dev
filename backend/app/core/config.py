"""
Configuration management using Pydantic Settings.
Loads environment variables with validation and defaults.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, ConfigDict
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All values are validated using Pydantic.
    """
    
    # API Configuration
    API_TITLE: str = Field(default="Hospital Appointment & Medical Record Management")
    API_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=False)
    
    # Server Configuration
    SERVER_HOST: str = Field(default="0.0.0.0")
    SERVER_PORT: int = Field(default=8000)
    
    # Database Configuration
    DB_USER: str = Field(default="postgres")
    DB_PASSWORD: str = Field(default="postgres")
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432)
    DB_NAME: str = Field(default="hospital_db")
    SQL_ECHO: bool = Field(default=False)
    DATABASE_URL: str = Field(default="")
    USE_SQLITE: bool = Field(default=True)
    
    # Security Configuration
    SECRET_KEY: str = Field(
        default="change-me-in-production-minimum-32-characters-long-please-!!!",
        description="Secret key for JWT token signing. Min 32 chars in production."
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8001,http://localhost:8002,http://localhost:8000",
        description="Comma-separated list of allowed origins"
    )
    
    # Appointment Reminder Configuration
    REMINDER_ENABLED: bool = Field(default=True)
    REMINDER_HOUR: int = Field(default=8)
    REMINDER_MINUTE: int = Field(default=0)
    REMINDER_HOURS_BEFORE: int = Field(default=24)
    
    # SMS/Email Configuration (for future integration)
    TWILIO_ACCOUNT_SID: str = Field(default="")
    TWILIO_AUTH_TOKEN: str = Field(default="")
    TWILIO_PHONE_NUMBER: str = Field(default="")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields from .env
    )
    
    def __init__(self, **data):
        """Initialize settings and parse ALLOWED_ORIGINS if string."""
        super().__init__(**data)
        
        # Handle ALLOWED_ORIGINS parsing
        if isinstance(self.ALLOWED_ORIGINS, str):
            self.ALLOWED_ORIGINS = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    def validate_secret_key_length(self) -> None:
        """Validate SECRET_KEY length in production mode."""
        if not self.DEBUG and len(self.SECRET_KEY) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters in production mode. "
                "Set DEBUG=true or update SECRET_KEY in .env"
            )


# Load settings on module import
settings = Settings()

# Validate in production
if not settings.DEBUG:
    settings.validate_secret_key_length()
