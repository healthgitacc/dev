"""
Department service - CRUD for departments under a hospital.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Department, Doctor, Hospital, HospitalUser, User
from app.core import NotFoundError, ConflictError, get_logger

logger = get_logger(__name__)


class DepartmentService:
    def __init__(self, db: Session):
        self.db = db

    def list_by_hospital(self, hospital_id: int) -> List[Department]:
        """List all departments for a hospital."""
        return self.db.query(Department).filter(Department.hospital_id == hospital_id).order_by(Department.name).all()

    def get(self, department_id: int) -> Optional[Department]:
        return self.db.query(Department).filter(Department.id == department_id).first()

    def get_by_hospital_and_name(self, hospital_id: int, name: str) -> Optional[Department]:
        return (
            self.db.query(Department)
            .filter(Department.hospital_id == hospital_id, Department.name == name.strip())
            .first()
        )

    @staticmethod
    def _normalize_department_label(value: str) -> str:
        normalized = " ".join((value or "").strip().lower().replace("-", " ").split())
        aliases = {
            "ortho": "orthopedics",
            "orthopaedics": "orthopedics",
            "cardio": "cardiology",
            "neuro": "neurology",
            "gen medicine": "general medicine",
            "general med": "general medicine",
            "uro": "urology",
        }
        return aliases.get(normalized, normalized)

    def sync_matching_doctors(self, hospital_id: int, department: Department) -> int:
        """
        Assign existing doctors to a department when their specialization matches
        the department name. This keeps newly created department admins able to
        see already existing doctors such as "General Medicine".
        """
        department_key = self._normalize_department_label(department.name)
        assigned = 0
        linked = 0

        doctors = (
            self.db.query(Doctor)
            .join(User, Doctor.user_id == User.id)
            .outerjoin(HospitalUser, HospitalUser.user_id == User.id)
            .filter(
                Doctor.user_id.isnot(None),
                func.lower(func.trim(Doctor.specialization)).isnot(None),
            )
            .all()
        )

        for doctor in doctors:
            specialization_key = self._normalize_department_label(doctor.specialization)
            if specialization_key != department_key:
                continue

            hospital_link = (
                self.db.query(HospitalUser)
                .filter(
                    HospitalUser.hospital_id == hospital_id,
                    HospitalUser.user_id == doctor.user_id,
                )
                .first()
            )
            any_link = (
                self.db.query(HospitalUser)
                .filter(HospitalUser.user_id == doctor.user_id)
                .first()
            )
            if any_link and not hospital_link:
                continue

            if doctor.department_id != department.id:
                doctor.department_id = department.id
                assigned += 1

            if doctor.user_id and not hospital_link:
                self.db.add(HospitalUser(hospital_id=hospital_id, user_id=doctor.user_id))
                linked += 1

        if assigned or linked:
            self.db.commit()
            self.db.refresh(department)
        else:
            self.db.flush()
        return assigned

    def create(self, hospital_id: int, name: str) -> Department:
        name = name.strip()
        if self.get_by_hospital_and_name(hospital_id, name):
            raise ConflictError(f"Department '{name}' already exists in this hospital", field="name")
        dept = Department(hospital_id=hospital_id, name=name)
        self.db.add(dept)
        self.db.commit()
        self.db.refresh(dept)
        self.sync_matching_doctors(hospital_id, dept)
        return dept

    def ensure_default_departments(self, hospital_id: int) -> None:
        """Create Ortho, Neuro, Uro if they don't exist for the hospital."""
        for name in ("Ortho", "Neuro", "Uro"):
            if not self.get_by_hospital_and_name(hospital_id, name):
                self.create(hospital_id, name)
