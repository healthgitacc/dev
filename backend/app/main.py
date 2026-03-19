"""
FastAPI Application Entry Point
Main application configuration and startup
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import os
import logging

from app.core import settings, app_exception_to_http, AppException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description="Production REST API for hospital appointment and medical record management",
    version=settings.API_VERSION,
)

# CORS Configuration - ADD BEFORE ROUTES
logger.info(f"CORS Allowed Origins: {settings.ALLOWED_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)


# Custom Middleware for Super Owner Access Control
from app.core.middleware import super_owner_access_control_middleware

@app.middleware("http")
async def super_owner_access_control(request: Request, call_next):
    """
    Middleware to enforce Super Owner access control.
    
    Blocks Super Owner from accessing patient, doctor, appointment, and medical record endpoints.
    """
    return await super_owner_access_control_middleware(request, call_next)


# Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom AppException."""
    logger.warning(f"AppException: {exc.code} - {exc.message}")
    http_exc = app_exception_to_http(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "code": "VALIDATION_ERROR",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "code": "INTERNAL_SERVER_ERROR",
        },
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info(f"[STARTUP] {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    
    # Initialize background scheduler for reminders
    try:
        from app.tasks import init_scheduler
        init_scheduler()
        logger.info("[OK] Background scheduler initialized")
    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    # Stop background scheduler
    try:
        from app.tasks import stop_scheduler
        stop_scheduler()
        logger.info("[OK] Background scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
    
    logger.info("[SHUTDOWN] Shutting down application")


# Health Check Routes
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Status and application info
    """
    return {
        "status": "ok",
        "message": "Hospital Management System is running",
        "environment": "development" if settings.DEBUG else "production",
    }


@app.get("/", tags=["Info"])
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        API title and version
    """
    return {
        "title": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


# Include API Routes
from app.routes import (
    auth_routes,
    user_routes,
    doctor_routes,
    patient_routes,
    appointment_routes,
    medical_record_routes,
    staff_routes,
    admin_doctor_routes,
    hospital_routes,
    department_routes,
    appointment_reminder_routes,
)

app.include_router(auth_routes.router, prefix="/api")
app.include_router(department_routes.router, prefix="/api")
app.include_router(staff_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")
app.include_router(doctor_routes.router, prefix="/api")
app.include_router(patient_routes.router, prefix="/api")
app.include_router(appointment_routes.router, prefix="/api")
app.include_router(medical_record_routes.router, prefix="/api")
app.include_router(admin_doctor_routes.router, prefix="/api")
app.include_router(hospital_routes.router, prefix="/api")
app.include_router(appointment_reminder_routes.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
    )
