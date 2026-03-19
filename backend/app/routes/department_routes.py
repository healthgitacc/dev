"""
Department and department-admin routes.
Hospital admin can list departments and create department admins.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core import (
    get_current_admin,
    get_current_hospital_admin_or_department_admin,
    get_hospital_id_for_user,
    AppException,
    app_exception_to_http,
    get_logger,
    ValidationError,
    ConflictError,
    AuthorizationError,
    generate_temporary_password,
)
from app.models import User, UserRole, HospitalUser
from app.schemas.auth import CreateDepartmentRequest, CreateDepartmentAdminRequest, CreateDepartmentAdminResponse
from app.services import UserService, DepartmentService, HospitalService
from app.core.security import PasswordManager

router = APIRouter(tags=["Departments"])
logger = get_logger(__name__)


@router.get(
    "/departments",
    response_model=dict,
)
async def list_departments(
    current_user: User = Depends(get_current_hospital_admin_or_department_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    List departments for the current user's hospital.
    Hospital admin and department admin can call this.
    """
    try:
        hospital_id = get_hospital_id_for_user(db, current_user)
        if not hospital_id and current_user.role == UserRole.HOSPITAL_ADMIN:
            hospital_id = HospitalService(db).get_or_create_hospital_for_admin(current_user)
        if not hospital_id:
            return {"items": []}
        dept_service = DepartmentService(db)
        departments = dept_service.list_by_hospital(hospital_id)
        return {
            "items": [
                {"id": d.id, "name": d.name, "hospital_id": d.hospital_id}
                for d in departments
            ]
        }
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.post(
    "/departments",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def create_department(
    body: CreateDepartmentRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Create a department (e.g. Ortho, Neuro, Uro) for your hospital. Hospital admin only.
    """
    try:
        if current_user.role != UserRole.HOSPITAL_ADMIN:
            raise AuthorizationError("Hospital admin access required")
        hospital_id = get_hospital_id_for_user(db, current_user)
        if not hospital_id:
            hospital_id = HospitalService(db).get_or_create_hospital_for_admin(current_user)
        if not hospital_id:
            raise ValidationError(
                "Your account could not be linked to a hospital. Please contact support.",
                field="hospital_id",
            )
        dept_service = DepartmentService(db)
        department = dept_service.create(hospital_id, body.name.strip())
        return {"id": department.id, "name": department.name, "hospital_id": department.hospital_id}
    except AppException as exc:
        raise app_exception_to_http(exc)


@router.post(
    "/admin/department-admins",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def create_department_admin(
    body: CreateDepartmentAdminRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    """
    Create a department admin user. Hospital admin only.
    Generates a temporary password; the new user should change it on first login.
    The new user is linked to the same hospital as the creating hospital admin.
    """
    try:
        if current_user.role != UserRole.HOSPITAL_ADMIN:
            raise AuthorizationError("Hospital admin access required")
        hospital_id = get_hospital_id_for_user(db, current_user)
        if not hospital_id:
            hospital_id = HospitalService(db).get_or_create_hospital_for_admin(current_user)
        if not hospital_id:
            raise ValidationError(
                "Your account could not be linked to a hospital. Please contact support.",
                field="hospital_id",
            )
        dept_service = DepartmentService(db)
        department = dept_service.get(body.department_id)
        if not department or department.hospital_id != hospital_id:
            raise ValidationError("Invalid department for your hospital", field="department_id")
        dept_service.sync_matching_doctors(hospital_id, department)
        user_service = UserService(db)
        if user_service.get_user_by_email(body.email):
            raise ConflictError(f"Email {body.email} already exists", field="email")
        temp_password = generate_temporary_password()
        password_hash = PasswordManager.hash_password(temp_password)
        new_user = User(
            name=body.name,
            email=body.email,
            phone=body.phone,
            password_hash=password_hash,
            role=UserRole.DEPARTMENT_ADMIN.value,
            is_active=True,
            department_id=body.department_id,
            created_by_id=current_user.id,
        )
        db.add(new_user)
        db.flush()
        db.add(HospitalUser(hospital_id=hospital_id, user_id=new_user.id))
        db.commit()
        db.refresh(new_user)
        return CreateDepartmentAdminResponse(
            user_id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            department_id=department.id,
            department_name=department.name,
            temporary_password=temp_password,
        ).dict()
    except AppException as exc:
        raise app_exception_to_http(exc)
