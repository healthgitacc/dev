"""
Base service class and service factory.
All business logic should be implemented in services, not in routes.
"""
from sqlalchemy.orm import Session
from typing import Generic, TypeVar, Optional, List
from app.core.logger import get_logger

T = TypeVar("T")

logger = get_logger(__name__)


class BaseService(Generic[T]):
    """
    Base service class providing common CRUD operations.
    Services should extend this class to implement business logic.
    """
    
    def __init__(self, db: Session, model: type[T]):
        """
        Initialize service.
        
        Args:
            db: Database session
            model: SQLAlchemy model class
        """
        self.db = db
        self.model = model
        self.logger = get_logger(self.__class__.__name__)
    
    def create(self, obj_in: dict) -> T:
        """
        Create a new record.
        
        Args:
            obj_in: Dictionary of attributes
            
        Returns:
            Created model instance
        """
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            self.logger.info(f"Created {self.model.__name__} with id {db_obj.id}")
            return db_obj
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise
    
    def get(self, id: int) -> Optional[T]:
        """
        Get a record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None
        """
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 10) -> tuple[List[T], int]:
        """
        Get all records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            Tuple of (records, total_count)
        """
        query = self.db.query(self.model)
        total = query.count()
        records = query.offset(skip).limit(limit).all()
        return records, total
    
    def update(self, id: int, obj_in: dict) -> Optional[T]:
        """
        Update a record.
        
        Args:
            id: Record ID
            obj_in: Dictionary of attributes to update
            
        Returns:
            Updated model instance or None
        """
        db_obj = self.get(id)
        if not db_obj:
            return None
        
        try:
            for field, value in obj_in.items():
                if value is not None:
                    setattr(db_obj, field, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            self.logger.info(f"Updated {self.model.__name__} with id {id}")
            return db_obj
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating {self.model.__name__} with id {id}: {str(e)}")
            raise
    
    def delete(self, id: int) -> bool:
        """
        Delete a record.
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        db_obj = self.get(id)
        if not db_obj:
            return False
        
        try:
            self.db.delete(db_obj)
            self.db.commit()
            self.logger.info(f"Deleted {self.model.__name__} with id {id}")
            return True
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error deleting {self.model.__name__} with id {id}: {str(e)}")
            raise
