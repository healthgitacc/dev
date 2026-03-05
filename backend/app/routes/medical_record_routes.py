"""
Medical record routes.
Handles medical record creation, updates, and retrieval.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.services import MedicalRecordService
from app.core import (
    get_current_user,
    AppException,
    app_exception_to_http,
    get_logger,
    validate_pagination,
)
from app.models import User

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])
logger = get_logger(__name__)


@router.get(
    "",
    response_model=dict,
)
async def list_medical_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get medical records (current user's context).
    
    - Patients see their own medical records
    - Doctors see records they created
    - Admins see all records
    
    Args:
        skip: Records to skip
        limit: Records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of medical records
    """
    try:
        from app.models import UserRole
        
        medical_record_service = MedicalRecordService(db)
        skip, limit = validate_pagination(skip, limit)
        
        # Get records based on user role
        if current_user.role == UserRole.PATIENT:
            # Patients see their own records
            from app.services import PatientService
            patient_service = PatientService(db)
            patient = patient_service.get_patient_by_user_id(current_user.id)
            if not patient:
                return {
                    "total": 0,
                    "skip": skip,
                    "limit": limit,
                    "items": [],
                }
            records, total = medical_record_service.get_patient_records(patient.id, skip, limit)
        elif current_user.role == UserRole.DOCTOR:
            # Doctors see records they created
            from app.services import DoctorService
            doctor_service = DoctorService(db)
            doctor = doctor_service.get_doctor_by_user_id(current_user.id)
            if not doctor:
                return {
                    "total": 0,
                    "skip": skip,
                    "limit": limit,
                    "items": [],
                }
            records, total = medical_record_service.get_doctor_records(doctor.id, skip, limit)
        else:
            # Admins see all records
            records, total = medical_record_service.get_all_records(skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": records,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def create_medical_record(
    patient_id: int = Query(..., gt=0, description="Patient ID"),
    disease_name: str = Query(..., min_length=3, max_length=255, description="Disease name"),
    diagnosis: str = Query(..., min_length=10, description="Medical diagnosis"),
    prescription_text: Optional[str] = Query(None, description="Prescription text"),
    dosage: Optional[str] = Query(None, max_length=255, description="Medication dosage"),
    follow_up_date: Optional[datetime] = Query(None, description="Follow-up date (UTC)"),
    notes: Optional[str] = Query(None, max_length=500, description="Additional notes"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Create a new medical record (doctor or admin only).
    
    Doctors can create records for their patients. Admins can create for any patient.
    
    Args:
        patient_id: Patient ID
        disease_name: Name of disease
        diagnosis: Medical diagnosis
        prescription_text: Prescription details
        dosage: Medication dosage
        follow_up_date: Follow-up appointment date
        notes: Additional notes
        current_user: Current authenticated user (doctor/admin)
        db: Database session
        
    Returns:
        Created medical record
        
    Raises:
        403 Forbidden: Not authorized
        404 Not Found: Patient not found
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError
        
        # Only doctors and admins can create records
        if current_user.role not in [UserRole.DOCTOR, UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN]:
            raise AuthorizationError("Doctor or admin access required")
        
        # Get doctor ID if doctor
        doctor_id = None
        if current_user.role == UserRole.DOCTOR:
            from app.services import DoctorService
            doctor_service = DoctorService(db)
            doctor = doctor_service.get_doctor_by_user_id(current_user.id)
            if doctor:
                doctor_id = doctor.id
        
        medical_record_service = MedicalRecordService(db)
        record = medical_record_service.create_medical_record(
            patient_id=patient_id,
            doctor_id=doctor_id,
            disease_name=disease_name,
            diagnosis=diagnosis,
            prescription_text=prescription_text,
            dosage=dosage,
            follow_up_date=follow_up_date,
            notes=notes,
        )
        
        return medical_record_service.get_record_with_details(record.id)
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/patient/{patient_id}",
    response_model=dict,
)
async def get_patient_medical_records(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get all medical records for a patient.
    
    Patients can only access their own records. Doctors and admins can access any.
    
    Args:
        patient_id: Patient ID
        skip: Records to skip
        limit: Records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of medical records
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError
        
        # Check authorization
        if current_user.role == UserRole.PATIENT:
            from app.services import PatientService
            patient_service = PatientService(db)
            patient = patient_service.get_patient_by_user_id(current_user.id)
            if not patient or patient.id != patient_id:
                raise AuthorizationError("Can only access your own medical records")
        
        medical_record_service = MedicalRecordService(db)
        skip, limit = validate_pagination(skip, limit)
        records, total = medical_record_service.get_patient_records(patient_id, skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": records,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/doctor/{doctor_id}",
    response_model=dict,
)
async def get_doctor_medical_records(
    doctor_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get all medical records created by a doctor.
    
    Doctors can only access their own records; admins can access any.
    
    Args:
        doctor_id: Doctor ID
        skip: Records to skip
        limit: Records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of medical records
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError
        
        # Check authorization
        if current_user.role == UserRole.DOCTOR:
            from app.services import DoctorService
            doctor_service = DoctorService(db)
            doctor = doctor_service.get_doctor_by_user_id(current_user.id)
            if not doctor or doctor.id != doctor_id:
                raise AuthorizationError("Can only access your own records")
        
        medical_record_service = MedicalRecordService(db)
        skip, limit = validate_pagination(skip, limit)
        records, total = medical_record_service.get_doctor_records(doctor_id, skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": records,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/{record_id}",
    response_model=dict,
)
async def get_medical_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get medical record by ID.
    
    Args:
        record_id: Medical record ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Medical record details
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError, NotFoundError
        
        medical_record_service = MedicalRecordService(db)
        record = medical_record_service.get(record_id)
        
        if not record:
            raise NotFoundError("MedicalRecord", record_id)
        
        # Check authorization
        if current_user.role == UserRole.PATIENT:
            if record.patient.user_id != current_user.id:
                raise AuthorizationError("Can only access your own medical records")
        elif current_user.role == UserRole.DOCTOR:
            if record.doctor and record.doctor.user_id != current_user.id:
                raise AuthorizationError("Can only access records you created")
        
        return medical_record_service.get_record_with_details(record_id)
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.put(
    "/{record_id}",
    response_model=dict,
)
async def update_medical_record(
    record_id: int,
    disease_name: Optional[str] = Query(None, min_length=3, max_length=255),
    diagnosis: Optional[str] = Query(None, min_length=10),
    prescription_text: Optional[str] = Query(None),
    dosage: Optional[str] = Query(None, max_length=255),
    follow_up_date: Optional[datetime] = Query(None),
    notes: Optional[str] = Query(None, max_length=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Update medical record (doctor or admin only).
    
    Args:
        record_id: Medical record ID
        disease_name: Updated disease name
        diagnosis: Updated diagnosis
        prescription_text: Updated prescription
        dosage: Updated dosage
        follow_up_date: Updated follow-up date
        notes: Updated notes
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated medical record
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError, NotFoundError
        
        # Only doctors and admins can update
        if current_user.role not in [UserRole.DOCTOR, UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN]:
            raise AuthorizationError("Doctor or admin access required")
        
        medical_record_service = MedicalRecordService(db)
        record = medical_record_service.get(record_id)
        
        if not record:
            raise NotFoundError("MedicalRecord", record_id)
        
        # Doctors can only update their own records
        if current_user.role == UserRole.DOCTOR:
            if not record.doctor or record.doctor.user_id != current_user.id:
                raise AuthorizationError("Can only update records you created")
        
        updated = medical_record_service.update_medical_record(
            record_id,
            disease_name=disease_name,
            diagnosis=diagnosis,
            prescription_text=prescription_text,
            dosage=dosage,
            follow_up_date=follow_up_date,
            notes=notes,
        )
        
        return medical_record_service.get_record_with_details(record_id)
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/list/follow-ups",
    response_model=dict,
)
async def get_follow_up_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get medical records with upcoming follow-up appointments.
    
    Useful for scheduling follow-up visits.
    
    Args:
        skip: Records to skip
        limit: Records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of records with follow-ups
    """
    try:
        medical_record_service = MedicalRecordService(db)
        skip, limit = validate_pagination(skip, limit)
        records, total = medical_record_service.get_follow_up_records(skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": records,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/search/disease",
    response_model=dict,
)
async def search_records_by_disease(
    disease: str = Query(..., min_length=2, description="Disease name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Search medical records by disease name.
    
    Args:
        disease: Disease name to search for
        skip: Records to skip
        limit: Records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated search results
    """
    try:
        medical_record_service = MedicalRecordService(db)
        skip, limit = validate_pagination(skip, limit)
        records, total = medical_record_service.get_records_by_disease(disease, skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": records,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/search/query",
    response_model=dict,
)
async def search_medical_records(
    q: str = Query(..., min_length=2, description="Search in disease name or diagnosis"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Search medical records by disease name or diagnosis.
    
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
        medical_record_service = MedicalRecordService(db)
        skip, limit = validate_pagination(skip, limit)
        records, total = medical_record_service.search_records(q, skip, limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": records,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)
