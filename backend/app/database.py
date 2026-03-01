"""
Database connection and session management.
Handles SQLAlchemy engine and session configuration.
"""
import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from app.core.config import settings

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

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection function for database sessions.
    Usage: Inject in FastAPI route as dependency.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Base class for all models
from sqlalchemy.orm import declarative_base
Base = declarative_base()

# Import all models to register them with SQLAlchemy
# This must happen after Base is defined
from app.models import User, Doctor, Patient, Appointment, MedicalRecord  # noqa: F401, E402
