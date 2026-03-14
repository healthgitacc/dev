"""
Hospital management routes for Super Owner.
Super Owner can manage hospitals only - no access to patient, doctor, or appointment data.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.db import get_db
from app.services import HospitalService
from app.core import (
    get_current_super_owner,
    AppException,
    app_exception_to_http,
    get_logger,
    validate_pagination,
)
from app.models import User, HospitalStatus
from datetime import datetime

router = APIRouter(prefix="/admin/hospitals", tags=["Hospital Management"])
logger = get_logger(__name__)


@router.get(
    "",
    response_model=dict,
    responses={403: {"description": "Super Owner access required"}},
)
async def list_hospitals(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by hospital status"),
    current_user: User = Depends(get_current_super_owner),
    db: Session = Depends(get_db),
) -> dict:
    """
    List all hospitals (Super Owner only).
    
    Super Owner can view all hospitals and filter by status.
    No access to patient, doctor, or appointment data.
    
    Args:
        skip: Records to skip
        limit: Records to return
        status: Filter by hospital status (active, inactive, pending)
        current_user: Current authenticated Super Owner user
        db: Database session
        
    Returns:
        Paginated list of hospitals
    """
    try:
        hospital_service = HospitalService(db)
        skip, limit = validate_pagination(skip, limit)
        
        # Parse status filter
        status_filter = None
        if status:
            try:
                status_filter = HospitalStatus(status)
            except ValueError:
                from app.core import ValidationError
                valid_statuses = [s.value for s in HospitalStatus]
                raise ValidationError(f"Status must be one of {valid_statuses}", field="status")
        
        hospitals, total = hospital_service.get_all_hospitals(skip, limit, status_filter)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": hospitals,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"description": "Super Owner access required"},
        409: {"description": "Hospital name or email already exists"},
    },
)
async def create_hospital(
    name: str = Query(..., min_length=2, max_length=255, description="Hospital name"),
    email: str = Query(..., description="Hospital email"),
    phone: Optional[str] = Query(None, description="Hospital phone number"),
    address: Optional[str] = Query(None, max_length=500, description="Hospital address"),
    current_user: User = Depends(get_current_super_owner),
    db: Session = Depends(get_db),
) -> dict:
    """
    Create a new hospital (Super Owner only).
    
    Super Owner can create new hospitals. Hospitals start as inactive.
    No patient, doctor, or appointment data is created.
    
    Args:
        name: Hospital name
        email: Hospital email
        phone: Hospital phone number
        address: Hospital address
        current_user: Current authenticated Super Owner user
        db: Database session
        
    Returns:
        Created hospital details
        
    Raises:
        403 Forbidden: Only Super Owner can create hospitals
        409 Conflict: Hospital name or email already exists
    """
    try:
        hospital_service = HospitalService(db)
        hospital = hospital_service.create_hospital(
            name=name,
            email=email,
            phone=phone,
            address=address,
        )
        
        logger.info(f"Hospital created by Super Owner {current_user.email}: {hospital.name}")
        
        return {
            "id": hospital.id,
            "name": hospital.name,
            "email": hospital.email,
            "phone": hospital.phone,
            "address": hospital.address,
            "status": hospital.status,
            "created_at": hospital.created_at.isoformat(),
            "message": "Hospital created successfully. Hospital is inactive by default.",
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/{hospital_id}",
    response_model=dict,
    responses={
        403: {"description": "Super Owner access required"},
        404: {"description": "Hospital not found"},
    },
)
async def get_hospital(
    hospital_id: int,
    current_user: User = Depends(get_current_super_owner),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get hospital details by ID (Super Owner only).
    
    Super Owner can view hospital details but not operational data.
    
    Args:
        hospital_id: Hospital ID
        current_user: Current authenticated Super Owner user
        db: Database session
        
    Returns:
        Hospital details
    """
    try:
        hospital_service = HospitalService(db)
        hospital = hospital_service.get_hospital(hospital_id)
        
        if not hospital:
            from app.core import NotFoundError
            raise NotFoundError("Hospital", hospital_id)
        
        return {
            "id": hospital.id,
            "name": hospital.name,
            "email": hospital.email,
            "phone": hospital.phone,
            "address": hospital.address,
            "status": hospital.status,
            "created_at": hospital.created_at.isoformat(),
            "updated_at": hospital.updated_at.isoformat(),
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.put(
    "/{hospital_id}/activate",
    response_model=dict,
    responses={
        403: {"description": "Super Owner access required"},
        404: {"description": "Hospital not found"},
    },
)
async def activate_hospital(
    hospital_id: int,
    current_user: User = Depends(get_current_super_owner),
    db: Session = Depends(get_db),
) -> dict:
    """
    Activate a hospital (Super Owner only).
    
    Changes hospital status to active, allowing hospital admin to operate.
    
    Args:
        hospital_id: Hospital ID to activate
        current_user: Current authenticated Super Owner user
        db: Database session
        
    Returns:
        Updated hospital details
    """
    try:
        hospital_service = HospitalService(db)
        hospital = hospital_service.activate_hospital(hospital_id)
        
        logger.info(f"Hospital activated by Super Owner {current_user.email}: {hospital.name}")
        
        return {
            "id": hospital.id,
            "name": hospital.name,
            "status": hospital.status,
            "message": "Hospital activated successfully. Hospital admin can now operate.",
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.put(
    "/{hospital_id}/deactivate",
    response_model=dict,
    responses={
        403: {"description": "Super Owner access required"},
        404: {"description": "Hospital not found"},
    },
)
async def deactivate_hospital(
    hospital_id: int,
    current_user: User = Depends(get_current_super_owner),
    db: Session = Depends(get_db),
) -> dict:
    """
    Deactivate a hospital (Super Owner only).
    
    Changes hospital status to inactive, preventing hospital admin operations.
    Does not delete hospital data.
    
    Args:
        hospital_id: Hospital ID to deactivate
        current_user: Current authenticated Super Owner user
        db: Database session
        
    Returns:
        Updated hospital details
    """
    try:
        hospital_service = HospitalService(db)
        hospital = hospital_service.deactivate_hospital(hospital_id)
        
        logger.info(f"Hospital deactivated by Super Owner {current_user.email}: {hospital.name}")
        
        return {
            "id": hospital.id,
            "name": hospital.name,
            "status": hospital.status,
            "message": "Hospital deactivated successfully. Hospital admin operations are now blocked.",
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.delete(
    "/{hospital_id}",
    response_model=dict,
    responses={
        403: {"description": "Super Owner access required"},
        404: {"description": "Hospital not found"},
    },
)
async def delete_hospital(
    hospital_id: int,
    current_user: User = Depends(get_current_super_owner),
    db: Session = Depends(get_db),
) -> dict:
    """
    Delete a hospital (Super Owner only).
    
    Completely removes hospital from system. Use with caution.
    This will also delete associated hospital admin accounts.
    
    Args:
        hospital_id: Hospital ID to delete
        current_user: Current authenticated Super Owner user
        db: Database session
        
    Returns:
        Success message
    """
    try:
        hospital_service = HospitalService(db)
        hospital = hospital_service.get_hospital(hospital_id)
        
        if not hospital:
            from app.core import NotFoundError
            raise NotFoundError("Hospital", hospital_id)
        
        hospital_service.delete_hospital(hospital_id)
        
        logger.info(f"Hospital deleted by Super Owner {current_user.email}: {hospital.name}")
        
        return {
            "message": f"Hospital '{hospital.name}' deleted successfully. All associated data has been removed.",
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/search/query",
    response_model=dict,
    responses={403: {"description": "Super Owner access required"}},
)
async def search_hospitals(
    q: str = Query(..., min_length=2, description="Search by name or email"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_super_owner),
    db: Session = Depends(get_db),
) -> dict:
    """
    Search hospitals by name or email (Super Owner only).
    
    Super Owner can search for hospitals by name or email.
    
    Args:
        q: Search query
        skip: Records to skip
        limit: Records to return
        current_user: Current authenticated Super Owner user
        db: Database session
        
    Returns:
        Paginated search results
    """
    try:
        hospital_service = HospitalService(db)
        skip, limit = validate_pagination(skip, limit)
        hospitals, total = hospital_service.search_hospitals(q, skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": hospitals,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/stats",
    response_model=dict,
    responses={403: {"description": "Super Owner access required"}},
)
async def get_hospital_stats(
    current_user: User = Depends(get_current_super_owner),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get hospital statistics (Super Owner only).
    
    Returns overview statistics for all hospitals.
    No patient, doctor, or appointment data is included.
    
    Args:
        current_user: Current authenticated Super Owner user
        db: Database session
        
    Returns:
        Hospital statistics
    """
    try:
        from sqlalchemy import func
        from app.models import Hospital, HospitalStatus
        
        # Count hospitals by status
        total_hospitals = db.query(func.count(Hospital.id)).scalar() or 0
        active_hospitals = db.query(func.count(Hospital.id)).filter(
            Hospital.status == HospitalStatus.ACTIVE
        ).scalar() or 0
        inactive_hospitals = db.query(func.count(Hospital.id)).filter(
            Hospital.status == HospitalStatus.INACTIVE
        ).scalar() or 0
        
        return {
            "total_hospitals": total_hospitals,
            "active_hospitals": active_hospitals,
            "inactive_hospitals": inactive_hospitals,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching hospital stats: {str(e)}")
        raise app_exception_to_http(
            AppException("Failed to fetch hospital statistics", "HOSPITAL_STATS_ERROR")
        )


