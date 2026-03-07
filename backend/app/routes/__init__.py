"""Routes - API endpoints."""
from app.routes import auth_routes, user_routes, doctor_routes, patient_routes, appointment_routes, medical_record_routes, staff_routes

__all__ = [
    "auth_routes",
    "user_routes",
    "doctor_routes",
    "patient_routes",
    "appointment_routes",
    "medical_record_routes",
    "staff_routes",
]
