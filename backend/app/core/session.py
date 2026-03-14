"""SQLAlchemy session factory configuration."""
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database import engine


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)