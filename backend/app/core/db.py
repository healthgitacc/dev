"""Database session dependency for FastAPI."""
from sqlalchemy.orm import Session
from typing import Generator

from app.core.session import SessionLocal


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