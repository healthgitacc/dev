"""
Doctor management routes.
Handles doctor profile and information endpoints.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.db import get_db
from app.services import DoctorService
from app.core import (
    get_current_user,
    get_current_admin,
    get_current_doctor,
    AppException,
    app_exception_to_http,
    get_logger,
    validate_pagination,
)
from app.models import User

router = APIRouter(prefix="/doctors", tags=["Doctors"])
logger = get_logger(__name__)


@router.get(
    "",
    response_model=dict,
)
async def list_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    List all active doctors.
    
    Public endpoint - accessible to all authenticated users except Super Owner.
    Super Owner is blocked from accessing doctor data.
    
    Args:
        skip: Records to skip
        limit: Records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of doctors with details
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError
        
        # Block Super Owner from accessing doctor data (privacy policy)
        if current_user.role == UserRole.SUPER_OWNER:
            raise AuthorizationError("Super Owner cannot access doctor data (privacy policy)")
        
        doctor_service = DoctorService(db)
        skip, limit = validate_pagination(skip, limit)
        department_id = getattr(current_user, "department_id", None) if current_user.role == UserRole.DEPARTMENT_ADMIN else None
        doctors, total = doctor_service.get_all_doctors(skip, limit, department_id=department_id)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": doctors,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/{doctor_id}",
    response_model=dict,
)
async def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """
    Get doctor details by ID.
    
    Public endpoint - accessible to all authenticated users.
    
    Args:
        doctor_id: Doctor ID
        db: Database session
        
    Returns:
        Doctor information with user details
    """
    try:
        doctor_service = DoctorService(db)
        doctor_info = doctor_service.get_doctor_with_user(doctor_id)
        
        if not doctor_info:
            from app.core import NotFoundError
            raise NotFoundError("Doctor", doctor_id)
        
        return doctor_info
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/search/specialization",
    response_model=dict,
)
async def search_doctors_by_specialization(
    specialization: str = Query(..., min_length=2, description="Medical specialization"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """
    Search doctors by specialization.
    
    Public endpoint - find doctors by their medical specialty.
    
    Args:
        specialization: Medical specialization keyword
        skip: Records to skip
        limit: Records to return
        db: Database session
        
    Returns:
        Paginated list of doctors
    """
    try:
        doctor_service = DoctorService(db)
        skip, limit = validate_pagination(skip, limit)
        doctors, total = doctor_service.get_doctors_by_specialization(specialization, skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": doctors,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/search/query",
    response_model=dict,
)
async def search_doctors(
    q: str = Query(..., min_length=2, description="Search by name, specialization, or email"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """
    Search doctors by name, specialization, or email.
    
    Public endpoint - multi-field search for doctors.
    
    Args:
        q: Search query
        skip: Records to skip
        limit: Records to return
        db: Database session
        
    Returns:
        Paginated search results
    """
    try:
        doctor_service = DoctorService(db)
        skip, limit = validate_pagination(skip, limit)
        doctors, total = doctor_service.search_doctors(q, skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": doctors,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/list/specializations",
    response_model=dict,
)
async def get_specializations(
    db: Session = Depends(get_db),
) -> dict:
    """
    Get list of all unique doctor specializations.
    
    Public endpoint - useful for filtering options.
    
    Args:
        db: Database session
        
    Returns:
        List of specializations
    """
    try:
        doctor_service = DoctorService(db)
        specializations = doctor_service.get_specializations()
        return {"specializations": specializations}
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.put(
    "/{doctor_id}",
    response_model=dict,
)
async def update_doctor_profile(
    doctor_id: int,
    name: Optional[str] = Query(None, min_length=2),
    specialization: Optional[str] = Query(None, min_length=2),
    experience_years: Optional[int] = Query(None, ge=0),
    license_number: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Update doctor profile (doctor or admin only).
    
    Doctors can only update their own profile; admins can update any doctor.
    
    Args:
        doctor_id: Doctor ID to update
        name: Doctor's professional name
        specialization: Medical specialization
        experience_years: Years of experience
        license_number: Medical license number
        current_user: Current user
        db: Database session
        
    Returns:
        Updated doctor information
    """
    try:
        from app.core import AuthorizationError, NotFoundError
        from app.models import UserRole
        
        # Check authorization
        doctor_service = DoctorService(db)
        doctor = doctor_service.get(doctor_id)
        
        if not doctor:
            raise NotFoundError("Doctor", doctor_id)
        
        if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN] and current_user.id != doctor.user_id:
            raise AuthorizationError("Can only update your own profile")
        
        updated_doctor = doctor_service.update_doctor_profile(
            doctor_id,
            name=name,
            specialization=specialization,
            experience_years=experience_years,
            license_number=license_number,
        )
        
        return doctor_service.get_doctor_with_user(doctor_id)
    except AppException as exc:
        raise app_exception_to_http(exc)
