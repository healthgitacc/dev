"""
Appointment reminder routes for hospital admins.
"""
from fastapi import APIRouter, Depends, Form, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

from app.core.db import get_db
from app.core import (
    AuthorizationError,
    AppException,
    ValidationError,
    app_exception_to_http,
    get_current_admin,
    get_hospital_id_for_user,
    get_logger,
    validate_pagination,
)
from app.models import User, UserRole
from app.services import AppointmentReminderService, HospitalService

router = APIRouter(tags=["Appointment Reminders"])
logger = get_logger(__name__)


class SendAppointmentRemindersRequest(BaseModel):
    appointment_ids: list[int] = Field(default_factory=list, min_length=1)


@router.get("/admin/reminders", response_model=dict)
async def list_appointment_reminders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    days_ahead: int = Query(7, ge=1, le=30),
    reminder_status: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    List upcoming reminder rows for the current hospital admin.
    """
    try:
        if current_user.role != UserRole.HOSPITAL_ADMIN:
            raise AuthorizationError("Hospital admin access required")

        hospital_id = get_hospital_id_for_user(db, current_user)
        if not hospital_id:
            hospital_id = HospitalService(db).get_or_create_hospital_for_admin(current_user)
        if not hospital_id:
            raise ValidationError("Hospital not found for current admin", field="hospital_id")

        skip, limit = validate_pagination(skip, limit)
        service = AppointmentReminderService(db)
        items, total = service.list_upcoming_reminders(
            hospital_id=hospital_id,
            skip=skip,
            limit=limit,
            days_ahead=days_ahead,
            status=reminder_status,
        )
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.post("/admin/reminders/send", response_model=dict, status_code=status.HTTP_200_OK)
async def send_appointment_reminders(
    body: SendAppointmentRemindersRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Send reminder SMS to one or more selected upcoming appointments.
    """
    try:
        if current_user.role != UserRole.HOSPITAL_ADMIN:
            raise AuthorizationError("Hospital admin access required")

        hospital_id = get_hospital_id_for_user(db, current_user)
        if not hospital_id:
            hospital_id = HospitalService(db).get_or_create_hospital_for_admin(current_user)
        if not hospital_id:
            raise ValidationError("Hospital not found for current admin", field="hospital_id")

        service = AppointmentReminderService(db)
        result = service.send_reminders(hospital_id=hospital_id, appointment_ids=body.appointment_ids)
        return {
            "message": f"Processed {len(body.appointment_ids)} reminders",
            **result,
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.post("/webhooks/sms-replies", include_in_schema=False)
async def receive_sms_reply(
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: Optional[str] = Form(None),
    db: Session = Depends(get_db),
) -> Response:
    """
    Twilio inbound SMS webhook. Updates reminder status when patient replies YES or NO.
    """
    try:
        logger.info("Incoming SMS reply webhook received from=%s body=%s sid=%s", From, Body, MessageSid)
        service = AppointmentReminderService(db)
        reminder = service.record_reply(from_phone=From, body=Body, inbound_message_id=MessageSid)
        if reminder:
            logger.info("Recorded SMS reply for reminder %s as %s", reminder.id, reminder.status)
        else:
            logger.warning("SMS reply received but no reminder matched from=%s body=%s", From, Body)
    except Exception as exc:
        logger.error("Failed to process SMS reply webhook: %s", str(exc))

    return Response(content="<Response></Response>", media_type="text/xml")
