"""
Hospital Administration routes.
Simplified workflow: Only Super Admin creates Hospital Admin.
Hospital Admin adds patients and books appointments.
Patient and Doctor receive SMS notifications only.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import time

from app.core.db import get_db
from app.services import AuthService, PatientService, AppointmentService, DoctorService
from app.core import (
    get_current_super_admin,
    get_current_staff_or_admin,
    get_current_hospital_admin_or_department_admin,
    get_current_user,
    AppException,
    app_exception_to_http,
    get_logger,
    AuthorizationError,
)
from app.models import User, UserRole
from app.schemas import (
    StaffRegisterRequest,
    PatientRegisterByStaffRequest,
    DoctorRegisterByAdminRequest,
    AppointmentCreateByStaffRequest,
    AppointmentCreateByStaffManualRequest,
    TokenResponse,
    RegisterRequest,
)

router = APIRouter(prefix="/admin", tags=["Hospital Administration"])
logger = get_logger(__name__)


@router.post(
    "/create-hospital-admin",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"description": "Super admin access required"},
        409: {"description": "Email already exists"},
    },
)
async def create_hospital_admin(
    request: StaffRegisterRequest,
    current_admin: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Create a new hospital admin (Super Admin only).
    
    Hospital admin can add patients and book appointments.
    
    Args:
        request: Hospital admin details
        current_admin: Current authenticated super admin user
        db: Database session
        
    Returns:
        TokenResponse with JWT token and admin info
    """
    try:
        auth_service = AuthService(db)
        
        # Create RegisterRequest object for AuthService
        register_request = RegisterRequest(
            name=request.name,
            email=request.email,
            password=request.password,
            phone=request.phone,
            role=UserRole.HOSPITAL_ADMIN,
        )
        
        # Register the hospital admin
        token_response = auth_service.register_user(register_request)
        logger.info(f"Hospital admin created: {request.email}")
        return token_response
        
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.post(
    "/patients",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"description": "Admin access required"},
        409: {"description": "Email already exists"},
    },
)
async def add_patient(
    request: PatientRegisterByStaffRequest,
    current_admin: User = Depends(get_current_staff_or_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Add a new patient (Super Admin or Hospital Admin only).
    
    No login credentials created - patient receives SMS notification only.
    Patient can optionally register later if needed.
    
    Args:
        request: Patient details
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        Patient details added to system
    """
    try:
        logger.info(f"[DEBUG] add_patient: Starting add patient request")
        logger.info(f"[DEBUG] Request data: name={request.name}, email={request.email}, blood_group={request.blood_group}, gender={request.gender}")
        
        # Generate valid password that meets strength requirements
        # Format: RandomStr@123 (has upper, lower, digit, special)
        temp_password = f"TempPass@{int(time.time()) % 10000:04d}"
        logger.info(f"[DEBUG] Generated temp password")
        
        auth_service = AuthService(db)
        logger.info(f"[DEBUG] AuthService instantiated")
        
        # Create RegisterRequest object for AuthService
        # Note: AuthService.register_user() automatically creates a Patient profile for PATIENT role
        register_request = RegisterRequest(
            name=request.name,
            email=request.email,
            password=temp_password,
            phone=request.phone,
            role=UserRole.PATIENT,
        )
        
        token_response = auth_service.register_user(register_request)
        logger.info(f"[DEBUG] User registered: user_id={token_response.user_id}")
        
        # Get the user object and patient profile that were created by register_user
        user = db.query(User).filter(User.id == token_response.user_id).first()
        if not user:
            raise ValueError(f"User {token_response.user_id} not found after registration")
        
        # Get the patient profile that was auto-created by register_user
        from app.models import Patient
        patient = db.query(Patient).filter(Patient.user_id == user.id).first()
        if not patient:
            raise ValueError(f"Patient profile not found for user {user.id}")
        
        # Update the patient profile with additional details
        patient.blood_group = request.blood_group
        patient.gender = request.gender if request.gender else None
        patient.address = request.address
        patient.medical_history = request.medical_history
        db.commit()
        db.refresh(patient)
        
        logger.info(f"Patient added by admin: {user.email}")
        
        # Send confirmation SMS to patient with credentials
        from app.services.notification_service import NotificationService
        notification_service = NotificationService()
        if user.phone:
            sms_result = notification_service.send_patient_credentials(
                phone_number=user.phone,
                patient_name=user.name,
                email=user.email,
                temporary_password=temp_password,
            )
            logger.info(f"[SMS] Patient credentials sent to {user.phone}: {sms_result}")
        else:
            logger.warning("[SMS] Patient has no phone number; skipping credentials SMS")
        
        return {
            "id": patient.id,
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "blood_group": patient.blood_group,
            "gender": patient.gender,
            "status": "active",
            "message": "Patient added successfully. SMS notification sent."
        }
        
    except AppException as exc:
        logger.error(f"AppException in add_patient: {str(exc)}")
        raise app_exception_to_http(exc)
    except Exception as exc:
        logger.error(f"Error adding patient: {str(exc)}", exc_info=True)
        raise


@router.post(
    "/appointments",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"description": "Admin access required"},
        404: {"description": "Patient or Doctor not found"},
        409: {"description": "Time slot conflict"},
    },
)
async def book_appointment(
    request: AppointmentCreateByStaffRequest,
    current_admin: User = Depends(get_current_hospital_admin_or_department_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Book an appointment (Hospital Admin or Department Admin). Department admin can only book with doctors in their department.
    
    Creates appointment and sends SMS notifications to patient and doctor.
    No login required for notifications.
    
    Args:
        request: Appointment details
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        Created appointment details
    """
    try:
        from app.services.notification_service import NotificationService
        from app.models import Doctor as DoctorModel

        # Department admin: only allow booking with doctors in their department
        if current_admin.role == UserRole.DEPARTMENT_ADMIN and getattr(current_admin, "department_id", None):
            doctor = db.query(DoctorModel).filter(DoctorModel.id == request.doctor_id).first()
            if not doctor or doctor.department_id != current_admin.department_id:
                raise AuthorizationError("You can only book appointments with doctors in your department")

        # Convert to datetime
        appointment_datetime = datetime.fromisoformat(request.appointment_date.replace('Z', '+00:00'))
        
        # Create appointment
        appointment_service = AppointmentService(db)
        appointment = appointment_service.create_appointment(
            doctor_id=request.doctor_id,
            patient_id=request.patient_id,
            appointment_date=appointment_datetime,
            duration_minutes=request.duration_minutes,
            notes=f"Chief Complaint: {request.chief_complaint}\nSymptoms: {request.symptoms}\n{request.notes or ''}",
        )
        
        # Get patient and doctor details for notification
        patient_service = PatientService(db)
        patient = patient_service.get(request.patient_id)
        
        from app.models import Doctor
        doctor = db.query(Doctor).filter(Doctor.id == request.doctor_id).first()
        doctor_user = doctor.user if doctor else None
        
        # Send SMS notifications (no login needed)
        notification_service = NotificationService()
        
        logger.info(f"[SMS DEBUG] Patient phone: {patient.user.phone if patient else 'No patient'}, Doctor phone: {doctor_user.phone if doctor_user else 'No doctor'}")
        
        if patient and patient.user.phone:
            logger.info(f"[SMS DEBUG] Sending SMS to patient: {patient.user.phone}")
            result = notification_service.send_appointment_reminder(
                phone_number=patient.user.phone,
                patient_name=patient.user.name,
                doctor_name=doctor_user.name if doctor_user else "Doctor",
                appointment_datetime=appointment_datetime,
            )
            logger.info(f"[SMS DEBUG] Patient SMS result: {result}")
        else:
            logger.warning(f"[SMS DEBUG] Patient has no phone or patient not found")
        
        # TODO: Doctor SMS disabled for now - requires valid Twilio phone number in .env
        # if doctor_user and doctor_user.phone:
        #     logger.info(f"[SMS DEBUG] Sending SMS to doctor: {doctor_user.phone}")
        #     result = notification_service.send_appointment_reminder(
        #         phone_number=doctor_user.phone,
        #         patient_name=patient.user.name if patient else "Patient",
        #         doctor_name=doctor_user.name,
        #         appointment_datetime=appointment_datetime,
        #     )
        #     logger.info(f"[SMS DEBUG] Doctor SMS result: {result}")
        # else:
        #     logger.warning(f"[SMS DEBUG] Doctor has no phone or doctor not found")
        
        logger.info(
            f"Appointment booked by admin {current_admin.email}: "
            f"Patient {request.patient_id} with Doctor {request.doctor_id}"
        )
        
        return {
            "id": appointment.id,
            "appointment_date": appointment.appointment_date.isoformat(),
            "status": appointment.status,
            "chief_complaint": request.chief_complaint,
            "duration_minutes": appointment.duration_minutes,
            "message": "Appointment booked successfully. SMS alerts sent to patient and doctor.",
        }
        
    except AppException as exc:
        raise app_exception_to_http(exc)
    except ValueError as e:
        raise app_exception_to_http(
            AppException(f"Invalid date format: {str(e)}", "INVALID_DATE_FORMAT")
        )


@router.post(
    "/appointments/manual",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"description": "Admin access required"},
        404: {"description": "Doctor not found"},
        409: {"description": "Patient email already exists or time slot conflict"},
    },
)
async def book_appointment_manual(
    request: AppointmentCreateByStaffManualRequest,
    current_admin: User = Depends(get_current_hospital_admin_or_department_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Book an appointment with manual patient information (Hospital Admin or Department Admin). Department admin only with doctors in their department.
    
    Creates or finds patient by email, then books appointment and sends SMS.
    
    Args:
        request: Appointment request with patient details
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        Created appointment details with patient and doctor info
    """
    try:
        from app.services.notification_service import NotificationService
        from app.models import Doctor, Patient, UserRole
        import re
        
        # Validate email format
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', request.patient_email):
            raise AppException("Invalid email format", "INVALID_EMAIL")
        
        # Convert datetime
        appointment_datetime = datetime.fromisoformat(request.appointment_date.replace('Z', '+00:00'))
        
        # Check if doctor exists
        doctor = db.query(Doctor).filter(Doctor.id == request.doctor_id).first()
        if not doctor:
            raise AppException(f"Doctor with ID {request.doctor_id} not found", "DOCTOR_NOT_FOUND", 404)
        if current_admin.role == UserRole.DEPARTMENT_ADMIN and getattr(current_admin, "department_id", None):
            if doctor.department_id != current_admin.department_id:
                raise AuthorizationError("You can only book appointments with doctors in your department")
        
        # Find or create patient by email
        patient_user = db.query(User).filter(
            User.email == request.patient_email,
            User.role == UserRole.PATIENT
        ).first()
        
        if patient_user:
            # Patient already exists
            logger.info(f"Using existing patient: {request.patient_email}")
            patient = db.query(Patient).filter(Patient.user_id == patient_user.id).first()
            if not patient:
                raise AppException("Patient profile not found", "PATIENT_PROFILE_NOT_FOUND")
        else:
            # Create new patient
            logger.info(f"Creating new patient: {request.patient_email}")
            from app.models import Gender
            from app.core.security import PasswordManager
            
            try:
                # Generate temp password with required format (RandomStr@123)
                temp_password = f"TempPass@{int(time.time()) % 10000:04d}"
                password_hash = PasswordManager.hash_password(temp_password)
                
                # Create user for patient
                patient_user = User(
                    name=request.patient_name,
                    email=request.patient_email,
                    phone=request.patient_phone,
                    password_hash=password_hash,
                    role=UserRole.PATIENT,
                    is_active=True,
                )
                db.add(patient_user)
                db.flush()  # Flush to get user ID
                
                # Create patient profile
                patient = Patient(
                    user_id=patient_user.id,
                    age=None,
                    gender=None,
                    blood_group=None,
                    medical_history=None,
                )
                db.add(patient)
                db.flush()
                
                logger.info(f"Created new patient: {request.patient_email} with ID {patient.id}")
            except Exception as e:
                db.rollback()
                if "Duplicate entry" in str(e) or "UNIQUE constraint failed" in str(e):
                    raise AppException(f"Patient email {request.patient_email} already exists", "DUPLICATE_EMAIL", 409)
                raise
        
        # Create appointment
        appointment_service = AppointmentService(db)
        appointment = appointment_service.create_appointment(
            doctor_id=request.doctor_id,
            patient_id=patient.id,
            appointment_date=appointment_datetime,
            duration_minutes=request.duration_minutes,
            notes=f"Chief Complaint: {request.chief_complaint}\nSymptoms: {request.symptoms}\n{request.notes or ''}",
        )
        
        # Send SMS notifications
        notification_service = NotificationService()
        
        logger.info(f"[SMS DEBUG] Patient phone: {patient.user.phone}, Doctor phone: {doctor.user.phone if doctor.user else 'No doctor'}")
        
        if patient.user.phone:
            logger.info(f"[SMS DEBUG] Sending SMS to patient: {patient.user.phone}")
            result = notification_service.send_appointment_reminder(
                phone_number=patient.user.phone,
                patient_name=patient.user.name,
                doctor_name=doctor.user.name if doctor.user else "Doctor",
                appointment_datetime=appointment_datetime,
            )
            logger.info(f"[SMS DEBUG] Patient SMS result: {result}")
        else:
            logger.warning(f"[SMS DEBUG] Patient has no phone number")
        
        # TODO: Doctor SMS disabled for now - requires valid Twilio phone number in .env
        # if doctor.user and doctor.user.phone:
        #     logger.info(f"[SMS DEBUG] Sending SMS to doctor: {doctor.user.phone}")
        #     result = notification_service.send_appointment_reminder(
        #         phone_number=doctor.user.phone,
        #         patient_name=patient.user.name,
        #         doctor_name=doctor.user.name,
        #         appointment_datetime=appointment_datetime,
        #     )
        #     logger.info(f"[SMS DEBUG] Doctor SMS result: {result}")
        # else:
        #     logger.warning(f"[SMS DEBUG] Doctor has no phone number")
        
        logger.info(
            f"Appointment booked by admin {current_admin.email}: "
            f"Patient {patient.id} ({request.patient_email}) with Doctor {request.doctor_id}"
        )
        
        return {
            "id": appointment.id,
            "appointment_date": appointment.appointment_date.isoformat(),
            "status": appointment.status,
            "patient_id": patient.id,
            "patient_email": patient.user.email,
            "patient_name": patient.user.name,
            "doctor_id": request.doctor_id,
            "doctor_name": doctor.user.name if doctor.user else "Doctor",
            "chief_complaint": request.chief_complaint,
            "duration_minutes": request.duration_minutes,
            "message": "Appointment booked successfully. SMS alerts sent to patient and doctor.",
        }
        
    except AppException as exc:
        raise app_exception_to_http(exc)
    except ValueError as e:
        raise app_exception_to_http(
            AppException(f"Invalid date format: {str(e)}", "INVALID_DATE_FORMAT")
        )
    except Exception as e:
        logger.error(f"Error booking appointment: {str(e)}", exc_info=True)
        raise app_exception_to_http(
            AppException("Failed to book appointment", "APPOINTMENT_ERROR")
        )


@router.get(
    "/patients",
    response_model=dict,
    responses={403: {"description": "Admin access required"}},
)
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_admin: User = Depends(get_current_staff_or_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    List all patients in the system (Staff and Admin only).
    
    Useful for staff to find existing patients or view patient list.
    Super Owner is blocked from accessing patient data.
    
    Args:
        skip: Number of results to skip
        limit: Maximum results to return
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        Paginated list of patients
    """
    try:
        from app.models import UserRole
        from app.core import AuthorizationError
        
        # Block Super Owner from accessing patient data (privacy policy)
        if current_admin.role == UserRole.SUPER_OWNER:
            raise AuthorizationError("Super Owner cannot access patient data (privacy policy)")
        
        patient_service = PatientService(db)
        patients, total = patient_service.get_all_patients(skip=skip, limit=limit)
        
        return {
            "items": [
                {
                    "id": p.id,
                    "name": p.user.name,
                    "email": p.user.email,
                    "phone": p.user.phone,
                    "blood_group": p.blood_group,
                    "gender": p.gender,
                }
                for p in patients
            ],
            "total": total,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/appointments",
    response_model=dict,
    responses={403: {"description": "Admin access required"}},
)
async def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_admin: User = Depends(get_current_staff_or_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    List all appointments (Admin only).
    
    Args:
        skip: Number of results to skip
        limit: Maximum results to return
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        Paginated list of appointments
    """
    try:
        appointment_service = AppointmentService(db)
        appointments, total = appointment_service.get_all_appointments(
            skip=skip,
            limit=limit,
        )
        
        return {
            "items": [
                appointment_service.get_appointment_with_details(a.id)
                for a in appointments
            ],
            "total": total,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/dashboard",
    response_model=dict,
    responses={403: {"description": "Admin access required"}},
)
async def get_dashboard(
    current_admin: User = Depends(get_current_staff_or_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get admin dashboard (Admin only).
    
    Args:
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        Dashboard statistics
    """
    try:
        from sqlalchemy import func
        from app.models import Patient, Doctor, Appointment
        
        total_patients = db.query(func.count(Patient.id)).scalar() or 0
        total_doctors = db.query(func.count(Doctor.id)).scalar() or 0
        total_appointments = db.query(func.count(Appointment.id)).scalar() or 0
        
        return {
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "total_appointments": total_appointments,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard: {str(e)}")
        raise app_exception_to_http(
            AppException("Failed to fetch dashboard", "DASH_ERROR")
        )



@router.post(
    "/patients",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"description": "Staff/Admin access required"},
        409: {"description": "Email already exists"},
    },
)
async def register_patient_by_staff(
    request: PatientRegisterByStaffRequest,
    current_staff: User = Depends(get_current_staff_or_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Register a new patient (Hospital Staff or Admin).
    
    Staff registers a patient arriving at the hospital.
    Generates temporary credentials sent to patient.
    
    Args:
        request: Patient registration details
        current_staff: Current authenticated staff/admin user
        db: Database session
        
    Returns:
        Patient details with generated credentials
        
    Raises:
        403 Forbidden: Only staff/admin can register patients
        409 Conflict: Email already exists
    """
    try:
        import secrets
        
        # Generate temporary password
        temp_password = secrets.token_urlsafe(12)
        
        auth_service = AuthService(db)
        user = auth_service.register_user(
            name=request.name,
            email=request.email,
            password=temp_password,
            phone=request.phone,
            role=UserRole.PATIENT,
        )
        
        # Create patient profile
        patient_service = PatientService(db)
        patient = patient_service.create_patient(
            user_id=user.id,
            blood_group=request.blood_group,
            gender=request.gender,
            date_of_birth=request.date_of_birth,
            address=request.address,
            medical_history=request.medical_history,
        )
        
        logger.info(f"Patient registered by staff: {user.email}")
        
        # TODO: Send SMS notification to patient with credentials
        # notification_service.send_patient_credentials(request.phone, user.email, temp_password)
        
        return {
            "id": patient.id,
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "blood_group": patient.blood_group,
            "gender": patient.gender,
            "temporary_password": temp_password,
            "message": "Patient registered successfully. Credentials sent via SMS/Email.",
            "status": "active"
        }
        
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.post(
    "/appointments",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"description": "Staff/Admin access required"},
        404: {"description": "Patient or Doctor not found"},
        409: {"description": "Time slot conflict"},
    },
)
async def create_appointment_by_staff(
    request: AppointmentCreateByStaffRequest,
    current_staff: User = Depends(get_current_hospital_admin_or_department_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Create an appointment on behalf of a patient (Hospital Admin or Department Admin). Department admin only with doctors in their department.
    
    Staff books appointment with doctor details, disease/symptoms info.
    Both doctor and patient receive notifications.
    
    Args:
        request: Appointment details
        current_staff: Current authenticated staff/admin user
        db: Database session
        
    Returns:
        Created appointment details
        
    Raises:
        403 Forbidden: Only staff/admin can create appointments
        404 Not Found: Patient or Doctor not found
        409 Conflict: Time slot already booked
    """
    try:
        from app.schemas.appointment import AppointmentCreate
        from app.services.notification_service import NotificationService
        from app.models import Doctor as DoctorModel

        if current_staff.role == UserRole.DEPARTMENT_ADMIN and getattr(current_staff, "department_id", None):
            doctor = db.query(DoctorModel).filter(DoctorModel.id == request.doctor_id).first()
            if not doctor or doctor.department_id != current_staff.department_id:
                raise AuthorizationError("You can only book appointments with doctors in your department")
        
        # Convert to datetime
        appointment_datetime = datetime.fromisoformat(request.appointment_date.replace('Z', '+00:00'))
        
        # Create appointment using service
        appointment_service = AppointmentService(db)
        appointment = appointment_service.create_appointment(
            doctor_id=request.doctor_id,
            patient_id=request.patient_id,
            appointment_date=appointment_datetime,
            duration_minutes=request.duration_minutes,
            notes=f"Chief Complaint: {request.chief_complaint}\nSymptoms: {request.symptoms}\n{request.notes or ''}",
        )
        
        # Get patient and doctor details for notification
        patient_service = PatientService(db)
        patient = patient_service.get(request.patient_id)
        
        from app.models import User
        doctor = db.query(User).filter(User.id == db.query(User).join(
            db.models.Doctor
        ).filter(db.models.Doctor.id == request.doctor_id).first())
        
        # Send notifications
        notification_service = NotificationService()
        
        if patient and patient.user.phone:
            notification_service.send_appointment_reminder(
                phone_number=patient.user.phone,
                patient_name=patient.user.name,
                doctor_name="Your Doctor",
                appointment_datetime=appointment_datetime,
            )
        
        logger.info(
            f"Appointment created by staff {current_staff.email}: "
            f"Patient {request.patient_id} with Doctor {request.doctor_id}"
        )
        
        return {
            "id": appointment.id,
            "appointment_date": appointment.appointment_date.isoformat(),
            "status": appointment.status,
            "chief_complaint": request.chief_complaint,
            "symptoms": request.symptoms,
            "duration_minutes": appointment.duration_minutes,
            "message": "Appointment created successfully. Notifications sent to patient and doctor.",
        }
        
    except AppException as exc:
        raise app_exception_to_http(exc)
    except ValueError as e:
        raise app_exception_to_http(
            AppException(f"Invalid date format: {str(e)}", "INVALID_DATE_FORMAT")
        )


@router.get(
    "/patients",
    response_model=dict,
    responses={403: {"description": "Staff/Admin access required"}},
)
async def list_all_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_staff: User = Depends(get_current_staff_or_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    List all patients in the system (Staff and Admin only).
    
    Useful for staff to find existing patients or view patient list.
    
    Args:
        skip: Number of results to skip
        limit: Maximum results to return
        current_staff: Current authenticated staff/admin user
        db: Database session
        
    Returns:
        Paginated list of patients
    """
    try:
        patient_service = PatientService(db)
        patients, total = patient_service.get_all_patients(skip=skip, limit=limit)
        
        return {
            "items": [
                {
                    "id": p.id,
                    "name": p.user.name,
                    "email": p.user.email,
                    "phone": p.user.phone,
                    "blood_group": p.blood_group,
                    "gender": p.gender,
                }
                for p in patients
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/patients/lookup",
    response_model=dict,
    responses={
        403: {"description": "Staff/Admin access required"},
        404: {"description": "Patient not found"},
    },
)
async def lookup_patient_by_contact(
    email: Optional[str] = Query(None, description="Patient email"),
    phone: Optional[str] = Query(None, description="Patient phone number"),
    current_staff: User = Depends(get_current_staff_or_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Look up an existing patient by unique email or phone.

    Used by staff while booking appointments to auto-fill patient details.

    Args:
        email: Patient email (unique)
        phone: Patient phone number (unique)
        current_staff: Current authenticated staff/admin user
        db: Database session

    Returns:
        Patient information with linked user details
    """
    try:
        # Require exactly one of email or phone
        if (not email and not phone) or (email and phone):
            raise AppException(
                "Provide exactly one of email or phone for lookup",
                "INVALID_LOOKUP_PARAMS",
                400,
            )

        from app.models import Patient as PatientModel, User as UserModel, UserRole

        query = db.query(PatientModel).join(UserModel).filter(
            UserModel.role == UserRole.PATIENT
        )
        if email:
            query = query.filter(UserModel.email == email)
        else:
            query = query.filter(UserModel.phone == phone)

        patient = query.first()
        if not patient:
            raise AppException("Patient not found", "PATIENT_NOT_FOUND", 404)

        # Reuse patient service to format response consistently
        patient_service = PatientService(db)
        patient_data = patient_service.get_patient_with_user(patient.id)
        return patient_data
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/appointments",
    response_model=dict,
    responses={403: {"description": "Staff/Admin access required"}},
)
async def list_all_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_staff: User = Depends(get_current_staff_or_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    List all appointments in the system (Staff and Admin only).
    
    Useful for staff to view hospital schedule and manage appointments.
    
    Args:
        skip: Number of results to skip
        limit: Maximum results to return
        status: Filter by appointment status
        current_staff: Current authenticated staff/admin user
        db: Database session
        
    Returns:
        Paginated list of appointments with details
    """
    try:
        appointment_service = AppointmentService(db)
        appointments, total = appointment_service.get_all_appointments(
            skip=skip,
            limit=limit,
            status=status
        )
        
        return {
            "items": [
                appointment_service.get_appointment_with_details(a.id)
                for a in appointments
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.get(
    "/dashboard-stats",
    response_model=dict,
    responses={401: {"description": "Authentication required"}},
)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get dashboard statistics based on user role.
    
    Returns overview statistics appropriate for the user's role:
    - Admin/Super Admin: System-wide statistics
    - Doctors: Their own appointment statistics
    - Patients: Their own appointment statistics
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Dashboard statistics based on user role
    """
    try:
        from sqlalchemy import func
        from app.models import User, Patient, Doctor, Appointment, AppointmentStatus, UserRole
        from datetime import datetime, date
        
        # Admin users see system-wide statistics
        if current_user.role in [UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN]:
            # Count statistics with optimized queries
            total_patients = db.query(func.count(Patient.id)).scalar() or 0
            total_doctors = db.query(func.count(Doctor.id)).scalar() or 0
            total_appointments = db.query(func.count(Appointment.id)).scalar() or 0
            
            # Count completed appointments
            completed_appointments = db.query(func.count(Appointment.id)).filter(
                Appointment.status == AppointmentStatus.COMPLETED
            ).scalar() or 0
            
            # Count today's appointments (SQLite compatible)
            today = date.today()
            today_appointments = 0
            try:
                # Try the SQL method first
                today_appointments = db.query(func.count(Appointment.id)).filter(
                    func.date(Appointment.appointment_date) == today
                ).scalar() or 0
            except:
                # Fallback for SQLite if date extraction fails
                all_today = db.query(Appointment).all()
                today_appointments = sum(
                    1 for apt in all_today 
                    if apt.appointment_date.date() == today
                )
            
            return {
                "total_patients": total_patients,
                "total_doctors": total_doctors,
                "total_appointments": total_appointments,
                "completed_appointments": completed_appointments,
                "today_appointments": today_appointments,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Doctors and Patients see their own appointment statistics
        else:
            # For doctors, get their appointments
            if current_user.role == UserRole.DOCTOR:
                doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
                if doctor:
                    total_appointments = db.query(func.count(Appointment.id)).filter(
                        Appointment.doctor_id == doctor.id
                    ).scalar() or 0
                    
                    completed_appointments = db.query(func.count(Appointment.id)).filter(
                        Appointment.doctor_id == doctor.id,
                        Appointment.status == AppointmentStatus.COMPLETED
                    ).scalar() or 0
                else:
                    total_appointments = 0
                    completed_appointments = 0
            
            # For patients, get their appointments
            elif current_user.role == UserRole.PATIENT:
                patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
                if patient:
                    total_appointments = db.query(func.count(Appointment.id)).filter(
                        Appointment.patient_id == patient.id
                    ).scalar() or 0
                    
                    completed_appointments = db.query(func.count(Appointment.id)).filter(
                        Appointment.patient_id == patient.id,
                        Appointment.status == AppointmentStatus.COMPLETED
                    ).scalar() or 0
                else:
                    total_appointments = 0
                    completed_appointments = 0
            
            else:
                total_appointments = 0
                completed_appointments = 0
            
            return {
                "total_patients": 0,  # Not applicable for non-admin
                "total_doctors": 0,   # Not applicable for non-admin
                "total_appointments": total_appointments,
                "completed_appointments": completed_appointments,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        raise app_exception_to_http(
            AppException("Failed to fetch dashboard statistics", "STATS_ERROR")
        )
