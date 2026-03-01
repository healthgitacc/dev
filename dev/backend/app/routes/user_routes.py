"""
User management routes.
Handles user CRUD operations (admin only).
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services import UserService
from app.core import (
    get_current_user,
    get_current_admin,
    AppException,
    app_exception_to_http,
    get_logger,
    validate_pagination,
)
from app.schemas import UserResponse, UserDetailResponse, PaginationParams
from app.models import User

router = APIRouter(prefix="/users", tags=["Users"])
logger = get_logger(__name__)


@router.get(
    "",
    response_model=dict,
    responses={
        403: {"description": "Admin access required"},
    },
)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    List all active users (admin only).
    
    Requires admin role. Returns paginated list of active users.
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return (max 100)
        current_user: Current admin user
        db: Database session
        
    Returns:
        Paginated list of users with total count
    """
    try:
        user_service = UserService(db)
        skip, limit = validate_pagination(skip, limit)
        users, total = user_service.get_active_users(skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": [UserResponse.from_orm(u).dict() for u in users],
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/{user_id}",
    response_model=dict,
    responses={
        403: {"description": "Forbidden - can only access own profile or admin"},
        404: {"description": "User not found"},
    },
)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get user details by ID.
    
    Users can only access their own profile unless they are admin.
    
    Args:
        user_id: User ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Detailed user information including role-specific profile
    """
    try:
        # Check authorization
        if current_user.id != user_id and current_user.role.value != "admin":
            from app.core import AuthorizationError
            raise AuthorizationError("Can only access your own profile")
        
        user_service = UserService(db)
        user = user_service.get(user_id)
        
        if not user:
            from app.core import NotFoundError
            raise NotFoundError("User", user_id)
        
        return UserDetailResponse.from_orm(user).dict()
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/search/by-role/{role}",
    response_model=dict,
)
async def search_users_by_role(
    role: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Search users by role (admin only).
    
    Args:
        role: User role (admin/doctor/patient)
        skip: Records to skip
        limit: Records to return
        current_user: Current admin user
        db: Database session
        
    Returns:
        Paginated user list
    """
    try:
        from app.models import UserRole
        
        # Validate role
        try:
            role_enum = UserRole(role)
        except ValueError:
            from app.core import ValidationError
            valid_roles = [r.value for r in UserRole]
            raise ValidationError(f"Role must be one of {valid_roles}", field="role")
        
        user_service = UserService(db)
        skip, limit = validate_pagination(skip, limit)
        users, total = user_service.get_users_by_role(role_enum, skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": [UserResponse.from_orm(u).dict() for u in users],
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/search/query",
    response_model=dict,
)
async def search_users(
    q: str = Query(..., min_length=2, description="Search query (name or email)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Search users by name or email (admin only).
    
    Args:
        q: Search query
        skip: Records to skip
        limit: Records to return
        current_user: Current admin user
        db: Database session
        
    Returns:
        Paginated search results
    """
    try:
        user_service = UserService(db)
        skip, limit = validate_pagination(skip, limit)
        users, total = user_service.search_users(q, skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": [UserResponse.from_orm(u).dict() for u in users],
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/stats/role-counts",
    response_model=dict,
)
async def get_user_statistics(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get user count statistics by role (admin only).
    
    Returns count of users in each role.
    """
    try:
        user_service = UserService(db)
        counts = user_service.count_users_by_role()
        return {"role_counts": counts}
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.post(
    "/{user_id}/deactivate",
    response_model=dict,
)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Deactivate a user account (admin only).
    
    Args:
        user_id: User ID to deactivate
        current_user: Current admin user
        db: Database session
        
    Returns:
        Updated user information
    """
    try:
        user_service = UserService(db)
        user = user_service.deactivate_user(user_id)
        return {"message": f"User {user.email} deactivated", "user_id": user.id}
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.post(
    "/{user_id}/activate",
    response_model=dict,
)
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Activate a user account (admin only).
    
    Args:
        user_id: User ID to activate
        current_user: Current admin user
        db: Database session
        
    Returns:
        Updated user information
    """
    try:
        user_service = UserService(db)
        user = user_service.activate_user(user_id)
        return {"message": f"User {user.email} activated", "user_id": user.id}
    except AppException as exc:
        raise app_exception_to_http(exc)
