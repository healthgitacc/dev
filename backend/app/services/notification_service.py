"""
Notification service for sending reminders via SMS and email.
Integrates with Twilio for SMS (mock implementation for dev).
"""
from typing import Optional, List
from datetime import datetime
import logging
from app.core import get_logger, settings

logger = get_logger(__name__)


class NotificationService:
    """Handle user notifications via SMS and email."""
    
    def __init__(self):
        """Initialize notification service."""
        self.sms_enabled = bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN)
        self.email_enabled = False  # Can be extended for email
        
        if self.sms_enabled and settings.DEBUG:
            logger.info("SMS notifications enabled (Twilio configured)")
        else:
            logger.info("SMS notifications disabled or in mock mode")
    
    def send_appointment_reminder(
        self,
        phone_number: str,
        patient_name: str,
        doctor_name: str,
        appointment_datetime: datetime,
    ) -> dict:
        """
        Send appointment reminder via SMS.
        
        Args:
            phone_number: Patient phone number
            patient_name: Patient name
            doctor_name: Doctor name
            appointment_datetime: Appointment date and time
            
        Returns:
            Dictionary with notification status
        """
        try:
            message_body = self._format_appointment_reminder(
                patient_name,
                doctor_name,
                appointment_datetime
            )
            
            if self.sms_enabled and not settings.DEBUG:
                # Production: Send via Twilio
                return self._send_twilio_sms(phone_number, message_body)
            else:
                # Development/Mock: Log to console
                return self._mock_send_sms(phone_number, message_body)
        
        except Exception as e:
            logger.error(f"Error sending appointment reminder: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message_id": None,
            }
    
    def send_bulk_reminders(
        self,
        reminders: List[dict],
    ) -> dict:
        """
        Send reminders to multiple patients.
        
        Args:
            reminders: List of reminder dictionaries with keys:
                      - phone_number
                      - patient_name
                      - doctor_name
                      - appointment_datetime
                      
        Returns:
            Summary of sending results
        """
        results = {
            "total": len(reminders),
            "sent": 0,
            "failed": 0,
            "errors": [],
        }
        
        for reminder in reminders:
            try:
                result = self.send_appointment_reminder(
                    phone_number=reminder.get("phone_number"),
                    patient_name=reminder.get("patient_name"),
                    doctor_name=reminder.get("doctor_name"),
                    appointment_datetime=reminder.get("appointment_datetime"),
                )
                
                if result.get("success"):
                    results["sent"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(result.get("error"))
            
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(str(e))
        
        logger.info(
            f"Bulk reminders sent: {results['sent']}/{results['total']} successful"
        )
        
        return results
    
    def _send_twilio_sms(self, phone_number: str, message_body: str) -> dict:
        """
        Send SMS via Twilio (production).
        
        Args:
            phone_number: Recipient phone number
            message_body: Message content
            
        Returns:
            Twilio response
        """
        try:
            from twilio.rest import Client
            
            # Log exactly what we're sending
            logger.info(f"[TWILIO DEBUG] Sending SMS from {settings.TWILIO_PHONE_NUMBER} to {phone_number}")
            logger.info(f"[TWILIO DEBUG] Message body:\n{message_body}")
            
            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            
            message = client.messages.create(
                body=message_body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number,
            )
            
            logger.info(f"✅ SMS sent to {phone_number}: {message.sid}")
            
            return {
                "success": True,
                "message_id": message.sid,
                "phone": phone_number,
            }
        except Exception as e:
            logger.error(f"Twilio SMS error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message_id": None,
            }
    
    def _mock_send_sms(self, phone_number: str, message_body: str) -> dict:
        """
        Mock SMS sending for development.
        
        Args:
            phone_number: Recipient phone number
            message_body: Message content
            
        Returns:
            Mock response
        """
        # In development, just log the message
        logger.info(
            f"\n{'='*60}\n"
            f"[MOCK SMS] To: {phone_number}\n"
            f"{message_body}\n"
            f"{'='*60}\n"
        )
        
        return {
            "success": True,
            "message_id": f"mock-{datetime.utcnow().timestamp()}",
            "phone": phone_number,
            "mock": True,
        }
    
    @staticmethod
    def _format_appointment_reminder(
        patient_name: str,
        doctor_name: str,
        appointment_datetime: datetime,
    ) -> str:
        """
        Format appointment reminder message.
        
        Args:
            patient_name: Patient name
            doctor_name: Doctor name
            appointment_datetime: Appointment date/time
            
        Returns:
            Formatted message
        """
        appointment_time = appointment_datetime.strftime("%B %d, %Y at %I:%M %p UTC")
        
        return (
            f"Hi {patient_name},\n\n"
            f"Reminder: You have an appointment with Dr. {doctor_name} "
            f"on {appointment_time}.\n\n"
            f"Please arrive 10 minutes early. Reply STOP to unsubscribe."
        )
    
    def send_appointment_confirmation(
        self,
        phone_number: str,
        patient_name: str,
        doctor_name: str,
        appointment_datetime: datetime,
    ) -> dict:
        """
        Send appointment confirmation after booking.
        
        Args:
            phone_number: Patient phone number
            patient_name: Patient name
            doctor_name: Doctor name
            appointment_datetime: Appointment date and time
            
        Returns:
            Dictionary with notification status
        """
        try:
            appointment_time = appointment_datetime.strftime("%B %d, %Y at %I:%M %p UTC")
            
            message_body = (
                f"Hi {patient_name},\n\n"
                f"Your appointment with Dr. {doctor_name} has been confirmed for "
                f"{appointment_time}.\n\n"
                f"Confirmation details have been sent to your email."
            )
            
            if self.sms_enabled and not settings.DEBUG:
                return self._send_twilio_sms(phone_number, message_body)
            else:
                return self._mock_send_sms(phone_number, message_body)
        
        except Exception as e:
            logger.error(f"Error sending confirmation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message_id": None,
            }
    
    def send_cancellation_notification(
        self,
        phone_number: str,
        patient_name: str,
        doctor_name: str,
        appointment_datetime: Optional[datetime] = None,
    ) -> dict:
        """
        Send appointment cancellation notification.
        
        Args:
            phone_number: Patient phone number
            patient_name: Patient name
            doctor_name: Doctor name
            appointment_datetime: Original appointment date and time
            
        Returns:
            Dictionary with notification status
        """
        try:
            if appointment_datetime:
                appointment_time = appointment_datetime.strftime("%B %d, %Y at %I:%M %p UTC")
                message_body = (
                    f"❌ APPOINTMENT CANCELLED\n\n"
                    f"Dear {patient_name},\n\n"
                    f"Your appointment with Dr. {doctor_name} scheduled for {appointment_time} "
                    f"has been cancelled.\n\n"
                    f"To reschedule, please:\n"
                    f"1. Call us at +1-800-HOSPITAL\n"
                    f"2. Use our online booking system\n"
                    f"3. Reply to this message\n\n"
                    f"We apologize for any inconvenience."
                )
            else:
                message_body = (
                    f"Hi {patient_name},\n\n"
                    f"Your appointment with Dr. {doctor_name} has been cancelled. "
                    f"Please contact us to reschedule."
                )
            
            if self.sms_enabled and not settings.DEBUG:
                return self._send_twilio_sms(phone_number, message_body)
            else:
                return self._mock_send_sms(phone_number, message_body)
        
        except Exception as e:
            logger.error(f"Error sending cancellation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message_id": None,
            }
