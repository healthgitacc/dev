"""
Admin doctor management routes.
Handles doctor creation and management by admins.
"""
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.db import get_db
from app.services import UserService, DoctorService, NotificationService, DepartmentService, HospitalService
from app.core import (
    get_current_admin,
    get_hospital_id_for_user,
    AppException,
    app_exception_to_http,
    get_logger,
    generate_temporary_password,
    validate_pagination,
)
from app.models import User, UserRole, Doctor, HospitalUser
from app.schemas import UserResponse, UserCreate
from app.schemas.admin import CreateDoctorRequest, UpdateDoctorRequest

router = APIRouter(prefix="/admin/doctors", tags=["Admin Doctors"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=dict,
    responses={
        403: {"description": "Admin access required"},
        409: {"description": "Email already registered"},
    },
)
async def create_doctor(
    request: CreateDoctorRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Create a new doctor account (admin only).
    
    Admins can create doctor accounts. A temporary password is generated
    and an SMS notification is sent to the doctor.
    
    Args:
        name: Doctor's professional name
        email: Doctor's email address
        phone: Doctor's phone number
        specialization: Medical specialization
        experience_years: Years of experience
        license_number: Medical license number
        current_user: Current admin user
        db: Database session
        
    Returns:
        Created doctor information
    """
    try:
        user_service = UserService(db)
        doctor_service = DoctorService(db)
        department_service = DepartmentService(db)
        notification_service = NotificationService()
        hospital_service = HospitalService(db)
        
        # Validate experience years
        if request.experience_years < 0:
            from app.core import ValidationError
            raise ValidationError("Experience years cannot be negative", field="experience_years")

        hospital_id = get_hospital_id_for_user(db, current_user)
        if not hospital_id:
            hospital_id = hospital_service.get_or_create_hospital_for_admin(current_user)
        department = department_service.get(request.department_id)
        if not department or department.hospital_id != hospital_id:
            from app.core import ValidationError
            raise ValidationError("Invalid department for your hospital", field="department_id")
        
        # Check if email already exists
        existing_user = user_service.get_user_by_email(request.email)
        if existing_user:
            from app.core import ConflictError
            raise ConflictError("Email already registered", field="email")
        
        # Generate temporary password
        temporary_password = generate_temporary_password()
        logger.info(f"Generated temporary password for doctor {request.name}: {temporary_password}")
        
        # Create user account
        user_create = UserCreate(
            name=request.name,
            email=request.email,
            password=temporary_password,  # Will be hashed in service
            role=UserRole.DOCTOR,
            phone=request.phone,
        )
        user = user_service.create_user(user_create)
        
        # Create doctor profile
        doctor_data = {
            "user_id": user.id,
            "department_id": request.department_id,
            "name": request.name,
            "specialization": request.specialization,
            "experience_years": request.experience_years,
            "license_number": request.license_number,
        }
        doctor = doctor_service.create(doctor_data)
        if hospital_id and not db.query(HospitalUser).filter(
            HospitalUser.hospital_id == hospital_id,
            HospitalUser.user_id == user.id,
        ).first():
            db.add(HospitalUser(hospital_id=hospital_id, user_id=user.id))
            db.commit()
            db.refresh(doctor)
        
        # Send welcome SMS to doctor
        try:
            notification_result = notification_service.send_doctor_welcome(
                phone_number=request.phone,
                doctor_name=request.name,
                specialization=request.specialization,
                email=request.email,
                temporary_password=temporary_password,
            )
            
            if notification_result.get("success"):
                logger.info(f"Welcome SMS sent to doctor {request.name} at {request.phone}")
            else:
                logger.warning(f"Failed to send SMS to doctor {request.name}: {notification_result.get('error')}")
        except Exception as e:
            logger.error(f"Error sending welcome SMS to doctor {request.name}: {str(e)}")
            # Don't fail the entire operation if SMS fails
        
        # Return doctor information
        doctor_info = doctor_service.get_doctor_with_user(doctor.id)
        return {
            "message": "Doctor created successfully",
            "doctor": doctor_info,
            "sms_sent": notification_result.get("success", False) if 'notification_result' in locals() else False,
        }
        
    except AppException as exc:
        raise app_exception_to_http(exc)
    except Exception as e:
        logger.error(f"Unexpected error creating doctor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create doctor account"
        )


@router.get(
    "",
    response_model=dict,
    responses={
        403: {"description": "Admin access required"},
    },
)
async def list_doctors_for_admin(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    List all doctors (admin only).
    Similar to the public doctor list but with admin access.
    """
    try:
        doctor_service = DoctorService(db)
        skip, limit = validate_pagination(skip, limit)
        doctors, total = doctor_service.get_all_doctors(skip, limit)
        
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
    responses={
        403: {"description": "Admin access required"},
        404: {"description": "Doctor not found"},
    },
)
async def get_doctor_for_admin(
    doctor_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get doctor details (admin only).
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


@router.put(
    "/{doctor_id}",
    response_model=dict,
    responses={
        403: {"description": "Admin access required"},
        404: {"description": "Doctor not found"},
    },
)
async def update_doctor_for_admin(
    doctor_id: int,
    name: Optional[str] = None,
    specialization: Optional[str] = None,
    experience_years: Optional[int] = None,
    license_number: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Update doctor profile (admin only).
    Admins can update any doctor's profile.
    """
    try:
        doctor_service = DoctorService(db)
        doctor = doctor_service.get(doctor_id)
        
        if not doctor:
            from app.core import NotFoundError
            raise NotFoundError("Doctor", doctor_id)
        
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


@router.delete(
    "/{doctor_id}",
    response_model=dict,
    responses={
        403: {"description": "Admin access required"},
        404: {"description": "Doctor not found"},
    },
)
async def deactivate_doctor(
    doctor_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Deactivate doctor account (admin only).
    Sets the associated user account to inactive.
    """
    try:
        user_service = UserService(db)
        doctor_service = DoctorService(db)
        
        # Get doctor to find associated user
        doctor = doctor_service.get(doctor_id)
        if not doctor:
            from app.core import NotFoundError
            raise NotFoundError("Doctor", doctor_id)
        
        # Deactivate the user account
        user = user_service.deactivate_user(doctor.user_id)
        
        return {
            "message": f"Doctor {user.name} deactivated successfully",
            "doctor_id": doctor_id,
            "user_id": user.id,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.post(
    "/{doctor_id}/activate",
    response_model=dict,
    responses={
        403: {"description": "Admin access required"},
        404: {"description": "Doctor not found"},
    },
)
async def activate_doctor(
    doctor_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Activate doctor account (admin only).
    Sets the associated user account to active.
    """
    try:
        user_service = UserService(db)
        doctor_service = DoctorService(db)
        
        # Get doctor to find associated user
        doctor = doctor_service.get(doctor_id)
        if not doctor:
            from app.core import NotFoundError
            raise NotFoundError("Doctor", doctor_id)
        
        # Activate the user account
        user = user_service.activate_user(doctor.user_id)
        
        return {
            "message": f"Doctor {user.name} activated successfully",
            "doctor_id": doctor_id,
            "user_id": user.id,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


