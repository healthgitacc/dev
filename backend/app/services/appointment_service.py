"""
Appointment service for appointment management.
Handles appointment creation, updates, and conflict detection.
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from app.models import Appointment, AppointmentStatus, Doctor, Patient, User
from app.services.base import BaseService
from app.core import (
    NotFoundError,
    AppointmentConflictError,
    InvalidAppointmentStatusError,
    ValidationError,
    paginate,
    get_logger,
)


logger = get_logger(__name__)


class AppointmentService(BaseService[Appointment]):
    """Service for appointment management."""
    
    def __init__(self, db: Session):
        """
        Initialize appointment service.
        
        Args:
            db: Database session
        """
        super().__init__(db, Appointment)
    
    def create_appointment(
        self,
        doctor_id: int,
        patient_id: int,
        appointment_date: datetime,
        duration_minutes: int = 30,
        notes: Optional[str] = None,
    ) -> Appointment:
        """
        Create a new appointment with conflict checking.
        
        Args:
            doctor_id: Doctor ID
            patient_id: Patient ID
            appointment_date: Appointment date and time
            duration_minutes: Appointment duration in minutes
            notes: Appointment notes
            
        Returns:
            Created appointment
            
        Raises:
            NotFoundError: If doctor or patient not found
            ValidationError: If appointment date is in the past
            AppointmentConflictError: If time slot is already booked
        """
        from datetime import timezone
        
        # Normalize appointment_date to be offset-aware in UTC for consistency
        if appointment_date.tzinfo is None:
            appointment_date = appointment_date.replace(tzinfo=timezone.utc)
        else:
            appointment_date = appointment_date.astimezone(timezone.utc)
        
        # Verify doctor exists
        # doctor_id can be either Doctor.id or User.id (for convenience)
        doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            # Try looking up by user_id
            doctor = self.db.query(Doctor).filter(Doctor.user_id == doctor_id).first()
        if not doctor:
            raise NotFoundError("Doctor", doctor_id)
        
        # Verify patient exists
        # patient_id can be either Patient.id or User.id (for convenience)
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            # Try looking up by user_id
            patient = self.db.query(Patient).filter(Patient.user_id == patient_id).first()
        if not patient:
            raise NotFoundError("Patient", patient_id)
        
        # Validate appointment date is in future
        # Use aware comparison (handle both naive and aware datetimes)
        now = datetime.now(timezone.utc)
        if appointment_date <= now:
            raise ValidationError("Appointment date must be in the future", field="appointment_date")
        
        # Check for doctor time slot conflicts
        self._check_doctor_availability(doctor.id, appointment_date, duration_minutes)
        
        # Check for patient existing appointments in same time
        self._check_patient_availability(patient.id, appointment_date, duration_minutes)
        
        try:
            appointment = Appointment(
                doctor_id=doctor.id,
                patient_id=patient.id,
                appointment_date=appointment_date,
                duration_minutes=duration_minutes,
                notes=notes,
                status=AppointmentStatus.SCHEDULED,
            )
            
            self.db.add(appointment)
            self.db.commit()
            self.db.refresh(appointment)
            
            logger.info(f"Appointment created: ID {appointment.id} for doctor {doctor_id}")
            
            return appointment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating appointment: {str(e)}")
            raise
    
    def _check_doctor_availability(
        self,
        doctor_id: int,
        appointment_date: datetime,
        duration_minutes: int,
    ) -> None:
        """
        Check if doctor has availability at the given time.
        
        Args:
            doctor_id: Doctor ID
            appointment_date: Proposed appointment date
            duration_minutes: Appointment duration
            
        Raises:
            AppointmentConflictError: If time slot is already booked
        """
        from datetime import timezone
        
        # Normalize appointment_date to be offset-aware in UTC
        if appointment_date.tzinfo is None:
            appointment_date = appointment_date.replace(tzinfo=timezone.utc)
        else:
            appointment_date = appointment_date.astimezone(timezone.utc)
        
        end_time = appointment_date + timedelta(minutes=duration_minutes)
        
        # Find overlapping appointments - get all existing appointments first
        existing_appointments = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.COMPLETED]),
        ).all()
        
        # Check for conflicts in Python
        for existing in existing_appointments:
            # Normalize existing appointment datetime
            existing_dt = existing.appointment_date
            if existing_dt.tzinfo is None:
                existing_dt = existing_dt.replace(tzinfo=timezone.utc)
            else:
                existing_dt = existing_dt.astimezone(timezone.utc)
            
            existing_end = existing_dt + timedelta(minutes=existing.duration_minutes)
            # Check if proposed appointment overlaps with existing
            if appointment_date < existing_end and end_time > existing_dt:
                raise AppointmentConflictError(
                    f"Doctor already has appointment from {existing_dt} to {existing_end}"
                )
    
    def _check_patient_availability(
        self,
        patient_id: int,
        appointment_date: datetime,
        duration_minutes: int,
    ) -> None:
        """
        Check if patient has availability at the given time.
        
        Args:
            patient_id: Patient ID
            appointment_date: Proposed appointment date
            duration_minutes: Appointment duration
            
        Raises:
            AppointmentConflictError: If patient has conflicting appointment
        """
        from datetime import timezone
        
        # Normalize appointment_date to be offset-aware in UTC
        if appointment_date.tzinfo is None:
            appointment_date = appointment_date.replace(tzinfo=timezone.utc)
        else:
            appointment_date = appointment_date.astimezone(timezone.utc)
        
        end_time = appointment_date + timedelta(minutes=duration_minutes)
        
        # Find overlapping appointments - get all existing appointments first
        existing_appointments = self.db.query(Appointment).filter(
            Appointment.patient_id == patient_id,
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.COMPLETED]),
        ).all()
        
        # Check for conflicts in Python
        for existing in existing_appointments:
            # Normalize existing appointment datetime
            existing_dt = existing.appointment_date
            if existing_dt.tzinfo is None:
                existing_dt = existing_dt.replace(tzinfo=timezone.utc)
            else:
                existing_dt = existing_dt.astimezone(timezone.utc)
            
            existing_end = existing_dt + timedelta(minutes=existing.duration_minutes)
            # Check if proposed appointment overlaps with existing
            if appointment_date < existing_end and end_time > existing_dt:
                raise AppointmentConflictError(
                    f"Patient already has appointment at {existing_dt}"
                )
    
    def get_appointment_with_details(self, appointment_id: int) -> Optional[dict]:
        """
        Get appointment with doctor and patient details.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            Dictionary with appointment and related info
        """
        appointment = self.get(appointment_id)
        if not appointment:
            return None
        
        return {
            "id": appointment.id,
            "doctor_id": appointment.doctor_id,
            "doctor_name": appointment.doctor.name,
            "doctor_specialization": appointment.doctor.specialization,
            "patient_id": appointment.patient_id,
            "patient_name": appointment.patient.user.name,
            "patient_email": appointment.patient.user.email,
            "appointment_date": appointment.appointment_date,
            "duration_minutes": appointment.duration_minutes,
            "status": appointment.status,
            "notes": appointment.notes,
            "reminder_sent": appointment.reminder_sent,
            "created_at": appointment.created_at,
            "updated_at": appointment.updated_at,
        }
    
    def get_doctor_appointments(
        self,
        doctor_id: int,
        skip: int = 0,
        limit: int = 10,
        status: Optional[AppointmentStatus] = None,
    ) -> tuple[List[dict], int]:
        """
        Get appointments for a doctor.
        
        Args:
            doctor_id: Doctor ID
            skip: Records to skip
            limit: Records to return
            status: Filter by appointment status
            
        Returns:
            Tuple of (appointments, total_count)
        """
        query = self.db.query(Appointment).filter(Appointment.doctor_id == doctor_id)
        
        if status:
            query = query.filter(Appointment.status == status)
        
        query = query.order_by(Appointment.appointment_date.desc())
        appointments, total = paginate(query, skip, limit)
        
        result = []
        for appointment in appointments:
            result.append(self.get_appointment_with_details(appointment.id))
        
        return result, total
    
    def get_patient_appointments(
        self,
        patient_id: int,
        skip: int = 0,
        limit: int = 10,
        status: Optional[AppointmentStatus] = None,
    ) -> tuple[List[dict], int]:
        """
        Get appointments for a patient.
        
        Args:
            patient_id: Patient ID
            skip: Records to skip
            limit: Records to return
            status: Filter by appointment status
            
        Returns:
            Tuple of (appointments, total_count)
        """
        query = self.db.query(Appointment).filter(Appointment.patient_id == patient_id)
        
        if status:
            query = query.filter(Appointment.status == status)
        
        query = query.order_by(Appointment.appointment_date.desc())
        appointments, total = paginate(query, skip, limit)
        
        result = []
        for appointment in appointments:
            result.append(self.get_appointment_with_details(appointment.id))
        
        return result, total
    
    def get_upcoming_appointments(
        self,
        doctor_id: Optional[int] = None,
        patient_id: Optional[int] = None,
        hours_ahead: int = 24,
    ) -> List[dict]:
        """
        Get upcoming appointments for reminder system.
        
        Args:
            doctor_id: Filter by doctor ID (optional)
            patient_id: Filter by patient ID (optional)
            hours_ahead: Look ahead this many hours
            
        Returns:
            List of upcoming appointments
        """
        now = datetime.utcnow()
        future_time = now + timedelta(hours=hours_ahead)
        
        query = self.db.query(Appointment).filter(
            Appointment.appointment_date >= now,
            Appointment.appointment_date <= future_time,
            Appointment.status == AppointmentStatus.SCHEDULED,
            Appointment.reminder_sent == None,
        )
        
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)
        
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        
        appointments = query.order_by(Appointment.appointment_date).all()
        
        result = []
        for appointment in appointments:
            result.append(self.get_appointment_with_details(appointment.id))
        
        return result
    
    def update_appointment_status(
        self,
        appointment_id: int,
        new_status: AppointmentStatus,
    ) -> Appointment:
        """
        Update appointment status with validation.
        
        Args:
            appointment_id: Appointment ID
            new_status: New status
            
        Returns:
            Updated appointment
            
        Raises:
            NotFoundError: If appointment not found
            InvalidAppointmentStatusError: If transition is invalid
        """
        appointment = self.get(appointment_id)
        if not appointment:
            raise NotFoundError("Appointment", appointment_id)
        
        # Convert string status to enum if needed
        current_status = AppointmentStatus(appointment.status) if isinstance(appointment.status, str) else appointment.status
        new_status_enum = AppointmentStatus(new_status) if isinstance(new_status, str) else new_status
        
        # Define valid status transitions
        valid_transitions = {
            AppointmentStatus.SCHEDULED: [
                AppointmentStatus.COMPLETED,
                AppointmentStatus.CANCELLED,
                AppointmentStatus.RESCHEDULED,
                AppointmentStatus.NO_SHOW,
            ],
            AppointmentStatus.COMPLETED: [],  # Cannot transition from completed
            AppointmentStatus.CANCELLED: [],  # Cannot transition from cancelled
            AppointmentStatus.NO_SHOW: [AppointmentStatus.RESCHEDULED],
            AppointmentStatus.RESCHEDULED: [AppointmentStatus.SCHEDULED],
        }
        
        if new_status_enum not in valid_transitions.get(current_status, []):
            raise InvalidAppointmentStatusError(
                current_status.value,
                new_status_enum.value
            )
        
        return super().update(appointment_id, {"status": new_status_enum.value})
    
    def reschedule_appointment(
        self,
        appointment_id: int,
        new_date: datetime,
        duration_minutes: Optional[int] = None,
    ) -> Appointment:
        """
        Reschedule an appointment.
        
        Args:
            appointment_id: Appointment ID
            new_date: New appointment date
            duration_minutes: New duration (optional, uses existing if not provided)
            
        Returns:
            Rescheduled appointment
            
        Raises:
            NotFoundError: If appointment not found
            ValidationError: If new date is invalid
        """
        appointment = self.get(appointment_id)
        if not appointment:
            raise NotFoundError("Appointment", appointment_id)
        
        if new_date <= datetime.utcnow():
            raise ValidationError("New appointment date must be in the future", field="new_date")
        
        duration = duration_minutes or appointment.duration_minutes
        
        # Check availability at new time
        self._check_doctor_availability(appointment.doctor_id, new_date, duration)
        self._check_patient_availability(appointment.patient_id, new_date, duration)
        
        return super().update(
            appointment_id,
            {
                "appointment_date": new_date,
                "duration_minutes": duration,
                "status": AppointmentStatus.RESCHEDULED,
            }
        )
    
    def mark_reminder_sent(self, appointment_id: int) -> Appointment:
        """
        Mark appointment reminder as sent.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            Updated appointment
        """
        return super().update(appointment_id, {"reminder_sent": datetime.utcnow()})
    
    def get_all_appointments(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
    ) -> tuple[List[Appointment], int]:
        """
        Get all appointments in the system (for staff/admin).
        
        Args:
            skip: Records to skip
            limit: Records to return
            status: Filter by appointment status
            
        Returns:
            Tuple of (appointments, total_count)
        """
        query = self.db.query(Appointment).order_by(Appointment.appointment_date.desc())
        
        if status:
            try:
                status_enum = AppointmentStatus(status)
                query = query.filter(Appointment.status == status_enum)
            except ValueError:
                pass  # Invalid status, ignore filter
        
        total = query.count()
        appointments = query.offset(skip).limit(limit).all()
        
        return appointments, total
