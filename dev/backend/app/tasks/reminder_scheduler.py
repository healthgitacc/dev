"""
Background task scheduler for appointment reminders.
Uses APScheduler to run reminder tasks at specified intervals.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.core import settings, get_logger

logger = get_logger(__name__)

# Global scheduler instance
scheduler: Optional[BackgroundScheduler] = None


def init_scheduler():
    """Initialize and start the background scheduler."""
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already initialized")
        return scheduler
    
    try:
        scheduler = BackgroundScheduler()
        
        # Add reminder job
        if settings.REMINDER_ENABLED:
            scheduler.add_job(
                send_appointment_reminders,
                CronTrigger(
                    hour=settings.REMINDER_HOUR,
                    minute=settings.REMINDER_MINUTE,
                ),
                id="appointment_reminders",
                name="Send appointment reminders",
                replace_existing=True,
                max_instances=1,
            )
            logger.info(
                f"Appointment reminder job scheduled for "
                f"{settings.REMINDER_HOUR:02d}:{settings.REMINDER_MINUTE:02d} UTC daily"
            )
        
        # Add cleanup job (every hour)
        scheduler.add_job(
            cleanup_old_reminders,
            CronTrigger(minute=0),
            id="cleanup_reminders",
            name="Cleanup old reminders",
            replace_existing=True,
            max_instances=1,
        )
        logger.info("Cleanup job scheduled to run hourly")
        
        scheduler.start()
        logger.info("Background scheduler started successfully")
        
        return scheduler
    
    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {str(e)}")
        raise


def stop_scheduler():
    """Stop the background scheduler."""
    global scheduler
    
    if scheduler and scheduler.running:
        try:
            scheduler.shutdown()
            logger.info("Background scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")


def send_appointment_reminders():
    """
    Background task to send appointment reminders.
    Runs daily at configured time.
    """
    try:
        from sqlalchemy.orm import Session
        from app.database import SessionLocal
        from app.services import AppointmentService
        from app.services.notification_service import NotificationService
        
        db = SessionLocal()
        
        try:
            appointment_service = AppointmentService(db)
            notification_service = NotificationService()
            
            # Get appointments in next 24 hours that haven't been reminded
            upcoming = appointment_service.get_upcoming_appointments(
                hours_ahead=settings.REMINDER_HOURS_BEFORE
            )
            
            logger.info(f"Found {len(upcoming)} appointments for reminders")
            
            # Prepare reminders
            reminders = []
            for apt in upcoming:
                # Check if patient has phone number
                if not apt.get("patient_email"):  # Using email field as proxy
                    continue
                
                reminders.append({
                    "phone_number": "+1234567890",  # In production, get from patient.user.phone
                    "patient_name": apt.get("patient_name"),
                    "doctor_name": apt.get("doctor_name"),
                    "appointment_datetime": apt.get("appointment_date"),
                    "appointment_id": apt.get("id"),
                })
            
            if not reminders:
                logger.info("No reminders to send")
                return
            
            # Send bulk reminders
            results = notification_service.send_bulk_reminders(reminders)
            
            # Mark reminders as sent in database
            for reminder in reminders:
                try:
                    appointment_service.mark_reminder_sent(reminder["appointment_id"])
                except Exception as e:
                    logger.error(f"Error marking reminder as sent: {str(e)}")
            
            logger.info(
                f"Reminder job completed: {results['sent']} sent, "
                f"{results['failed']} failed"
            )
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in appointment reminder job: {str(e)}", exc_info=True)


def cleanup_old_reminders():
    """
    Cleanup old reminder records.
    Removes reminders older than 90 days.
    """
    try:
        from sqlalchemy.orm import Session
        from app.database import SessionLocal
        from app.models import Appointment, AppointmentStatus
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        
        try:
            # Find and clean up old appointments (>90 days)
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            
            old_appointments = db.query(Appointment).filter(
                Appointment.appointment_date < cutoff_date,
                Appointment.status.in_([AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]),
            ).count()
            
            logger.info(f"Found {old_appointments} old appointments for cleanup")
            
            # In production, you might archive these instead of deleting
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in cleanup job: {str(e)}", exc_info=True)


def schedule_custom_reminder(appointment_id: int, send_at: datetime):
    """
    Schedule a custom reminder for a specific appointment.
    
    Args:
        appointment_id: Appointment ID
        send_at: DateTime to send reminder
    """
    global scheduler
    
    if not scheduler:
        logger.warning("Scheduler not initialized")
        return False
    
    try:
        job_id = f"reminder_{appointment_id}_{send_at.timestamp()}"
        
        scheduler.add_job(
            send_single_reminder,
            trigger="date",
            run_date=send_at,
            args=[appointment_id],
            id=job_id,
            replace_existing=True,
            max_instances=1,
        )
        
        logger.info(f"Scheduled custom reminder for appointment {appointment_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error scheduling custom reminder: {str(e)}")
        return False


def send_single_reminder(appointment_id: int):
    """
    Send reminder for a single appointment.
    
    Args:
        appointment_id: Appointment ID
    """
    try:
        from sqlalchemy.orm import Session
        from app.database import SessionLocal
        from app.services import AppointmentService
        from app.services.notification_service import NotificationService
        
        db = SessionLocal()
        
        try:
            appointment_service = AppointmentService(db)
            appointment = appointment_service.get(appointment_id)
            
            if not appointment:
                logger.warning(f"Appointment {appointment_id} not found")
                return
            
            # Get appointment details
            apt_details = appointment_service.get_appointment_with_details(appointment_id)
            
            # Send reminder
            notification_service = NotificationService()
            
            # In production, get actual phone number from patient
            phone_number = appointment.patient.user.phone or "+1234567890"
            
            result = notification_service.send_appointment_reminder(
                phone_number=phone_number,
                patient_name=apt_details["patient_name"],
                doctor_name=apt_details["doctor_name"],
                appointment_datetime=apt_details["appointment_date"],
            )
            
            if result.get("success"):
                appointment_service.mark_reminder_sent(appointment_id)
                logger.info(f"Reminder sent for appointment {appointment_id}")
            else:
                logger.error(f"Failed to send reminder: {result.get('error')}")
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error sending single reminder: {str(e)}", exc_info=True)


# Scheduler lifecycle management
def get_scheduler() -> Optional[BackgroundScheduler]:
    """Get the global scheduler instance."""
    return scheduler
