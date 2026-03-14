"""SQLAlchemy engine configuration."""
from sqlalchemy import create_engine, event
from sqlalchemy.pool import NullPool
from app.core.config import settings
import os

def create_sqlalchemy_engine() -> object:
    """Create and configure SQLAlchemy engine."""
    # Construct database URL
    if settings.USE_SQLITE or (settings.DATABASE_URL and "sqlite" in settings.DATABASE_URL.lower()):
        DATABASE_URL = "sqlite:///./hospital.db"
    elif settings.DATABASE_URL:
        DATABASE_URL = settings.DATABASE_URL
    else:
        DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

    # Create SQLAlchemy engine
    if "sqlite" in DATABASE_URL:
        # SQLite configuration
        engine = create_engine(
            DATABASE_URL,
            echo=os.getenv("SQL_ECHO", "false").lower() == "true",
            connect_args={"check_same_thread": False},
        )
    else:
        # PostgreSQL configuration
        engine = create_engine(
            DATABASE_URL,
            echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # Log SQL queries in dev
            pool_pre_ping=True,  # Verify connections before using them
            pool_recycle=3600,   # Recycle connections hourly
        )

    return engine


# Create engine on module import
engine = create_sqlalchemy_engine()