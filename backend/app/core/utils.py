"""
Utility functions for the application.
Includes helpers for pagination, response formatting, and data manipulation.
"""
from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Query
from app.schemas import PaginationParams

T = TypeVar("T")


class PaginatedResponse(Generic[T]):
    """Generic paginated response container."""
    
    def __init__(self, items: List[T], total: int, skip: int, limit: int):
        self.items = items
        self.total = total
        self.skip = skip
        self.limit = limit
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "total": self.total,
            "skip": self.skip,
            "limit": self.limit,
            "items": self.items
        }


def paginate(
    query: Query,
    skip: int = 0,
    limit: int = 10
) -> tuple[List, int]:
    """
    Paginate a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        skip: Number of records to skip
        limit: Number of records to return
        
    Returns:
        Tuple of (items, total_count)
    """
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def validate_pagination(skip: int, limit: int) -> tuple[int, int]:
    """
    Validate pagination parameters.
    
    Args:
        skip: Skip count
        limit: Limit count
        
    Returns:
        Validated (skip, limit) tuple
    """
    skip = max(0, skip)
    limit = max(1, min(limit, 100))  # Limit between 1 and 100
    return skip, limit


def filter_model_dict(
    obj,
    include_fields: Optional[List[str]] = None,
    exclude_fields: Optional[List[str]] = None
) -> dict:
    """
    Convert model to dict with field filtering.
    
    Args:
        obj: SQLAlchemy model instance
        include_fields: List of fields to include (if set, only these are included)
        exclude_fields: List of fields to exclude
        
    Returns:
        Filtered dictionary
    """
    from sqlalchemy.inspection import inspect
    
    # Get all columns
    mapper = inspect(type(obj))
    data = {}
    
    for column in mapper.columns:
        attr_name = column.name
        
        # Apply include filter
        if include_fields and attr_name not in include_fields:
            continue
        
        # Apply exclude filter
        if exclude_fields and attr_name in exclude_fields:
            continue
        
        data[attr_name] = getattr(obj, attr_name)
    
    return data


def format_datetime_response(dt) -> str:
    """
    Format datetime for API response.
    
    Args:
        dt: datetime object
        
    Returns:
        ISO format string
    """
    if dt:
        return dt.isoformat()
    return None


def generate_error_response(code: str, message: str, details: Optional[dict] = None) -> dict:
    """
    Generate standardized error response.
    
    Args:
        code: Error code
        message: Error message
        details: Additional error details
        
    Returns:
        Error response dictionary
    """
    response = {
        "code": code,
        "message": message,
    }
    
    if details:
        response["details"] = details
    
    return response
