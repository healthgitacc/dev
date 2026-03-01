"""
Patient management routes.
Handles patient profile and information endpoints.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services import PatientService
from app.core import (
    get_current_user,
    get_current_admin,
    AppException,
    app_exception_to_http,
    get_logger,
    validate_pagination,
)
from app.models import User

router = APIRouter(prefix="/patients", tags=["Patients"])
logger = get_logger(__name__)


@router.get(
    "",
    response_model=dict,
)
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    List all active patients.
    
    Accessible to authenticated doctors and admins.
    
    Args:
        skip: Records to skip
        limit: Records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of patients with details
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError
        
        # Allow Super Admin, Hospital Admin, and Doctors to view patient list
        # Patients can only view themselves
        if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN, UserRole.DOCTOR]:
            raise AuthorizationError("Super admin, hospital admin, or doctor access required to view patient details")
        
        patient_service = PatientService(db)
        skip, limit = validate_pagination(skip, limit)
        patients, total = patient_service.get_all_patients(skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": patients,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/{patient_id}",
    response_model=dict,
)
async def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get patient details by ID.
    
    Patients can only access their own profile; doctors and admins can access any patient.
    
    Args:
        patient_id: Patient ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Patient information with user details
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError, NotFoundError
        
        # Hospital Admin CANNOT view patient details (privacy policy)
        if current_user.role == UserRole.HOSPITAL_ADMIN:
            raise AuthorizationError("Hospital admin cannot view patient details (privacy policy)")
        
        patient_service = PatientService(db)
        patient = patient_service.get(patient_id)
        
        if not patient:
            raise NotFoundError("Patient", patient_id)
        
        # Check authorization - Only super admin, doctors, or the patient themselves can view
        if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.DOCTOR]:
            if current_user.id != patient.user_id:
                raise AuthorizationError("Can only access your own profile")
        
        patient_info = patient_service.get_patient_with_user(patient_id)
        return patient_info
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/search/query",
    response_model=dict,
)
async def search_patients(
    q: str = Query(..., min_length=2, description="Search by name or email"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Search patients by name or email.
    
    Accessible to authenticated doctors and admins.
    
    Args:
        q: Search query
        skip: Records to skip
        limit: Records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated search results
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError
        
        # Check authorization
        if current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
            raise AuthorizationError("Doctor or admin access required")
        
        patient_service = PatientService(db)
        skip, limit = validate_pagination(skip, limit)
        patients, total = patient_service.search_patients(q, skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": patients,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/filter/blood-group",
    response_model=dict,
)
async def get_patients_by_blood_group(
    blood_group: str = Query(..., description="Blood group (O+, O-, A+, A-, B+, B-, AB+, AB-)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get patients by blood group.
    
    Accessible to doctors and admins.
    
    Args:
        blood_group: Blood group filter
        skip: Records to skip
        limit: Records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated results
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError
        
        # Check authorization
        if current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
            raise AuthorizationError("Doctor or admin access required")
        
        patient_service = PatientService(db)
        skip, limit = validate_pagination(skip, limit)
        patients, total = patient_service.get_patients_by_blood_group(blood_group, skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": patients,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/filter/gender",
    response_model=dict,
)
async def get_patients_by_gender(
    gender: str = Query(..., description="Gender (male, female, other)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get patients by gender.
    
    Accessible to doctors and admins.
    
    Args:
        gender: Gender filter
        skip: Records to skip
        limit: Records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated results
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError
        
        # Check authorization
        if current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
            raise AuthorizationError("Doctor or admin access required")
        
        patient_service = PatientService(db)
        skip, limit = validate_pagination(skip, limit)
        patients, total = patient_service.get_patients_by_gender(gender, skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": patients,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.put(
    "/{patient_id}",
    response_model=dict,
)
async def update_patient_profile(
    patient_id: int,
    age: Optional[int] = Query(None, ge=0, le=150),
    gender: Optional[str] = Query(None, description="male, female, or other"),
    blood_group: Optional[str] = Query(None),
    medical_history: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Update patient profile.
    
    Patients can only update their own profile; admins can update any patient.
    
    Args:
        patient_id: Patient ID to update
        age: Patient age
        gender: Patient gender
        blood_group: Patient blood group
        medical_history: Patient medical history
        current_user: Current user
        db: Database session
        
    Returns:
        Updated patient information
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError, NotFoundError
        
        # Check authorization
        patient_service = PatientService(db)
        patient = patient_service.get(patient_id)
        
        if not patient:
            raise NotFoundError("Patient", patient_id)
        
        if current_user.role != UserRole.ADMIN and current_user.id != patient.user_id:
            raise AuthorizationError("Can only update your own profile")
        
        updated_patient = patient_service.update_patient_profile(
            patient_id,
            age=age,
            gender=gender,
            blood_group=blood_group,
            medical_history=medical_history,
        )
        
        return patient_service.get_patient_with_user(patient_id)
    except AppException as exc:
        raise app_exception_to_http(exc)
