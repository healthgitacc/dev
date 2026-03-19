"""
Database connection and session management.
Handles SQLAlchemy engine and session configuration.
"""
import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from app.core.engine import engine

# Base class for all models - moved to bottom to avoid circular imports
from app.models.base import Base

# Import all models to register them with SQLAlchemy
# This must happen after Base is defined
from app.models import (  # noqa: F401, E402
    User,
    Doctor,
    Patient,
    Appointment,
    MedicalRecord,
    Hospital,
    HospitalUser,
    Department,
)
