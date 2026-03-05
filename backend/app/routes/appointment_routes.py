"""
Appointment management routes.
Handles appointment booking, updates, and scheduling.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.services import AppointmentService
from app.core import (
    get_current_user,
    get_current_doctor_or_patient,
    AppException,
    app_exception_to_http,
    get_logger,
    validate_pagination,
)
from app.models import User, AppointmentStatus

# Pydantic model for appointment creation
class AppointmentCreate(BaseModel):
    doctor_id: int = Field(..., gt=0, description="Doctor ID")
    appointment_date: datetime = Field(..., description="Appointment date and time (UTC)")
    duration_minutes: int = Field(30, ge=15, le=120, description="Appointment duration in minutes")
    notes: Optional[str] = Field(None, max_length=500, description="Appointment notes")

router = APIRouter(prefix="/appointments", tags=["Appointments"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_doctor_or_patient),
    db: Session = Depends(get_db),
) -> dict:
    """
    Create a new appointment.
    
    Patients can book appointments with doctors. Checks for time conflicts.
    
    Args:
        doctor_id: Doctor ID
        appointment_date: Appointment date and time (UTC)
        duration_minutes: Duration in minutes
        notes: Optional appointment notes
        current_user: Current authenticated user (patient)
        db: Database session
        
    Returns:
        Created appointment details
        
    Raises:
        404 Not Found: Doctor or patient not found
        409 Conflict: Time slot already booked
        422 Unprocessable Entity: Date in past or validation error
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError
        
        # Only patients can create appointments
        if current_user.role != UserRole.PATIENT:
            raise AuthorizationError("Only patients can book appointments")
        
        # Get patient ID from current user
        from app.services import PatientService
        patient_service = PatientService(db)
        patient = patient_service.get_patient_by_user_id(current_user.id)
        
        if not patient:
            raise AppException("Patient profile not found", "PATIENT_NOT_FOUND")
        
        appointment_service = AppointmentService(db)
        appointment = appointment_service.create_appointment(
            doctor_id=appointment_data.doctor_id,
            patient_id=patient.id,
            appointment_date=appointment_data.appointment_date,
            duration_minutes=appointment_data.duration_minutes,
            notes=appointment_data.notes,
        )
        
        return appointment_service.get_appointment_with_details(appointment.id)
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "",
    response_model=dict,
)
async def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    List appointments for current user.
    
    - Doctors see their appointments
    - Patients see their appointments
    - Admins see all appointments
    
    Args:
        skip: Records to skip
        limit: Records to return
        status: Filter by appointment status
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of appointments
    """
    try:
        from app.models import UserRole
        
        appointment_service = AppointmentService(db)
        skip, limit = validate_pagination(skip, limit)
        
        # Parse status filter
        status_filter = None
        if status:
            try:
                status_filter = AppointmentStatus(status)
            except ValueError:
                from app.core import ValidationError
                valid_statuses = [s.value for s in AppointmentStatus]
                raise ValidationError(f"Status must be one of {valid_statuses}", field="status")
        
        # Get appropriate appointments based on role
        if current_user.role == UserRole.DOCTOR:
            from app.services import DoctorService
            doctor_service = DoctorService(db)
            doctor = doctor_service.get_doctor_by_user_id(current_user.id)
            appointments, total = appointment_service.get_doctor_appointments(
                doctor.id, skip, limit, status_filter
            )
        elif current_user.role == UserRole.PATIENT:
            from app.services import PatientService
            patient_service = PatientService(db)
            patient = patient_service.get_patient_by_user_id(current_user.id)
            appointments, total = appointment_service.get_patient_appointments(
                patient.id, skip, limit, status_filter
            )
        else:  # Admin
            query = db.query(Appointment)
            if status_filter:
                query = query.filter(Appointment.status == status_filter)
            query = query.order_by(Appointment.appointment_date.desc())
            appointment_objs, total = paginate(query, skip, limit)
            appointments = [appointment_service.get_appointment_with_details(a.id) for a in appointment_objs]
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": appointments,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/{appointment_id}",
    response_model=dict,
)
async def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get appointment details.
    
    Users can only access their own appointments; admins can access any.
    
    Args:
        appointment_id: Appointment ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Appointment details
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError, NotFoundError
        
        appointment_service = AppointmentService(db)
        appointment = appointment_service.get(appointment_id)
        
        if not appointment:
            raise NotFoundError("Appointment", appointment_id)
        
        # Check authorization
        if current_user.role in [UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN]:
            pass  # Admins can view any appointment
        elif current_user.role == UserRole.DOCTOR:
            if appointment.doctor.user_id != current_user.id:
                raise AuthorizationError("Can only view your own appointments")
        else:  # Patient
            if appointment.patient.user_id != current_user.id:
                raise AuthorizationError("Can only view your own appointments")
        
        return appointment_service.get_appointment_with_details(appointment_id)
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.put(
    "/{appointment_id}/status",
    response_model=dict,
)
async def update_appointment_status(
    appointment_id: int,
    new_status: str = Query(..., description="New appointment status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Update appointment status (doctor or admin only).
    
    Args:
        appointment_id: Appointment ID
        new_status: New status
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated appointment
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError, NotFoundError
        
        # Only doctors and admins can update status
        if current_user.role not in [UserRole.DOCTOR, UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN]:
            raise AuthorizationError("Doctor or admin access required")
        
        # Parse status
        try:
            status_enum = AppointmentStatus(new_status)
        except ValueError:
            from app.core import ValidationError
            valid_statuses = [s.value for s in AppointmentStatus]
            raise ValidationError(f"Status must be one of {valid_statuses}", field="new_status")
        
        appointment_service = AppointmentService(db)
        appointment = appointment_service.get(appointment_id)
        
        if not appointment:
            raise NotFoundError("Appointment", appointment_id)
        
        # Doctors can only update their own appointments
        if current_user.role == UserRole.DOCTOR:
            if appointment.doctor.user_id != current_user.id:
                raise AuthorizationError("Can only update your own appointments")
        
        updated = appointment_service.update_appointment_status(appointment_id, status_enum)
        return appointment_service.get_appointment_with_details(appointment_id)
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.post(
    "/{appointment_id}/reschedule",
    response_model=dict,
)
async def reschedule_appointment(
    appointment_id: int,
    new_date: datetime = Query(..., description="New appointment date and time (UTC)"),
    duration_minutes: Optional[int] = Query(None, ge=15, le=120),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Reschedule an appointment (patient or admin).
    
    Args:
        appointment_id: Appointment ID
        new_date: New appointment date and time
        duration_minutes: New duration (optional)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Rescheduled appointment
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError, NotFoundError
        
        appointment_service = AppointmentService(db)
        appointment = appointment_service.get(appointment_id)
        
        if not appointment:
            raise NotFoundError("Appointment", appointment_id)
        
        # Check authorization
        if current_user.role in [UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN]:
            pass  # Admins can reschedule any
        elif current_user.role == UserRole.PATIENT:
            if appointment.patient.user_id != current_user.id:
                raise AuthorizationError("Can only reschedule your own appointments")
        else:
            raise AuthorizationError("Patient or admin access required")
        
        updated = appointment_service.reschedule_appointment(
            appointment_id,
            new_date,
            duration_minutes
        )
        
        return appointment_service.get_appointment_with_details(appointment_id)
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.post(
    "/{appointment_id}/cancel",
    response_model=dict,
)
async def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Cancel an appointment and send SMS notification to patient.
    
    Args:
        appointment_id: Appointment ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Cancelled appointment with notification status
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError, NotFoundError
        from app.services import NotificationService
        
        appointment_service = AppointmentService(db)
        appointment = appointment_service.get(appointment_id)
        
        if not appointment:
            raise NotFoundError("Appointment", appointment_id)
        
        # Check authorization
        if current_user.role in [UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN]:
            pass
        elif current_user.role == UserRole.PATIENT:
            if appointment.patient.user_id != current_user.id:
                raise AuthorizationError("Can only cancel your own appointments")
        elif current_user.role == UserRole.DOCTOR:
            if appointment.doctor.user_id != current_user.id:
                raise AuthorizationError("Can only cancel your own appointments")
        
        updated = appointment_service.update_appointment_status(
            appointment_id,
            AppointmentStatus.CANCELLED
        )
        
        # Send SMS notification to patient
        notification_service = NotificationService()
        sms_result = notification_service.send_cancellation_notification(
            phone_number=appointment.patient.user.phone or "",
            patient_name=appointment.patient.user.name,
            doctor_name=appointment.doctor.user.name,
            appointment_datetime=appointment.appointment_date,
        )
        
        logger.info(f"Appointment {appointment_id} cancelled. SMS notification: {sms_result.get('success')}")
        
        return {
            "message": "Appointment cancelled successfully",
            "appointment": appointment_service.get_appointment_with_details(appointment_id),
            "notification": {
                "sms_sent": sms_result.get("success"),
                "phone": sms_result.get("phone"),
            }
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.post(
    "/{appointment_id}/complete",
    response_model=dict,
)
async def complete_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Mark an appointment as completed (doctor or admin only).
    
    Args:
        appointment_id: Appointment ID
        current_user: Current authenticated user (must be doctor or admin)
        db: Database session
        
    Returns:
        Completed appointment
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError, NotFoundError
        
        # Only doctors and admins can complete appointments
        if current_user.role not in [UserRole.DOCTOR, UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN]:
            raise AuthorizationError("Doctor or admin access required")
        
        appointment_service = AppointmentService(db)
        appointment = appointment_service.get(appointment_id)
        
        if not appointment:
            raise NotFoundError("Appointment", appointment_id)
        
        # Doctors can only complete their own appointments
        if current_user.role == UserRole.DOCTOR:
            if appointment.doctor.user_id != current_user.id:
                raise AuthorizationError("Can only complete your own appointments")
        
        updated = appointment_service.update_appointment_status(
            appointment_id,
            AppointmentStatus.COMPLETED
        )
        
        return {
            "message": "Appointment marked as completed",
            "appointment": appointment_service.get_appointment_with_details(appointment_id)
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/upcoming/reminders",
    response_model=dict,
)
async def get_upcoming_appointments_for_reminders(
    hours_ahead: int = Query(24, ge=1, le=72),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get upcoming appointments for reminder system (internal use).
    
    Returns appointments in next N hours that haven't been reminded yet.
    
    Args:
        hours_ahead: Look ahead this many hours
        db: Database session
        
    Returns:
        List of upcoming appointments
    """
    try:
        appointment_service = AppointmentService(db)
        appointments = appointment_service.get_upcoming_appointments(hours_ahead=hours_ahead)
        
        return {
            "total": len(appointments),
            "hours_ahead": hours_ahead,
            "items": appointments,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


# Import at module level for type hints
from app.models import Appointment
from app.core import paginate
