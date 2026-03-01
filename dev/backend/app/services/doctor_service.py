"""
Doctor service for doctor-specific operations.
Handles doctor profile management and doctor-related queries.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import Doctor, User, UserRole
from app.services.base import BaseService
from app.core import (
    NotFoundError,
    ValidationError,
    paginate,
    get_logger,
)


logger = get_logger(__name__)


class DoctorService(BaseService[Doctor]):
    """Service for doctor management."""
    
    def __init__(self, db: Session):
        """
        Initialize doctor service.
        
        Args:
            db: Database session
        """
        super().__init__(db, Doctor)
    
    def get_doctor_by_user_id(self, user_id: int) -> Optional[Doctor]:
        """
        Get doctor by user ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Doctor object or None
        """
        return self.db.query(Doctor).filter(Doctor.user_id == user_id).first()
    
    def get_doctor_with_user(self, doctor_id: int) -> Optional[dict]:
        """
        Get doctor with associated user information.
        
        Args:
            doctor_id: Doctor ID
            
        Returns:
            Dictionary with doctor and user info
        """
        doctor = self.get(doctor_id)
        if not doctor:
            return None
        
        return {
            "id": doctor.id,
            "user_id": doctor.user_id,
            "name": doctor.user.name,
            "email": doctor.user.email,
            "phone": doctor.user.phone,
            "specialization": doctor.specialization,
            "experience_years": doctor.experience_years,
            "license_number": doctor.license_number,
            "is_active": doctor.user.is_active,
            "created_at": doctor.created_at,
        }
    
    def get_doctors_by_specialization(
        self,
        specialization: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[dict], int]:
        """
        Get doctors by specialization.
        
        Args:
            specialization: Medical specialization
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (doctors, total_count)
        """
        query = self.db.query(Doctor).filter(
            Doctor.specialization.ilike(f"%{specialization}%")
        )
        doctors, total = paginate(query, skip, limit)
        
        result = []
        for doctor in doctors:
            result.append(self.get_doctor_with_user(doctor.id))
        
        return result, total
    
    def get_all_doctors(self, skip: int = 0, limit: int = 10) -> tuple[List[dict], int]:
        """
        Get all active doctors.
        
        Args:
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (doctors, total_count)
        """
        query = self.db.query(Doctor).join(User).filter(User.is_active == True)
        doctors, total = paginate(query, skip, limit)
        
        result = []
        for doctor in doctors:
            result.append(self.get_doctor_with_user(doctor.id))
        
        return result, total
    
    def update_doctor_profile(
        self,
        doctor_id: int,
        specialization: Optional[str] = None,
        experience_years: Optional[int] = None,
        license_number: Optional[str] = None,
    ) -> Optional[Doctor]:
        """
        Update doctor profile information.
        
        Args:
            doctor_id: Doctor ID
            specialization: Medical specialization
            experience_years: Years of experience
            license_number: Medical license number
            
        Returns:
            Updated doctor object
            
        Raises:
            NotFoundError: If doctor not found
        """
        doctor = self.get(doctor_id)
        if not doctor:
            raise NotFoundError("Doctor", doctor_id)
        
        # Validate experience years
        if experience_years is not None:
            if experience_years < 0:
                raise ValidationError("Experience years cannot be negative", field="experience_years")
        
        update_data = {}
        if specialization is not None:
            update_data["specialization"] = specialization
        if experience_years is not None:
            update_data["experience_years"] = experience_years
        if license_number is not None:
            update_data["license_number"] = license_number
        
        if update_data:
            return super().update(doctor_id, update_data)
        
        return doctor
    
    def get_doctor_by_license_number(self, license_number: str) -> Optional[Doctor]:
        """
        Get doctor by license number.
        
        Args:
            license_number: Medical license number
            
        Returns:
            Doctor object or None
        """
        return self.db.query(Doctor).filter(
            Doctor.license_number == license_number
        ).first()
    
    def search_doctors(
        self,
        query: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[dict], int]:
        """
        Search doctors by name, specialization, or email.
        
        Args:
            query: Search query
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (doctors, total_count)
        """
        search = f"%{query}%"
        q = self.db.query(Doctor).join(User).filter(
            (User.name.ilike(search)) |
            (Doctor.specialization.ilike(search)) |
            (User.email.ilike(search))
        )
        doctors, total = paginate(q, skip, limit)
        
        result = []
        for doctor in doctors:
            result.append(self.get_doctor_with_user(doctor.id))
        
        return result, total
    
    def get_specializations(self) -> List[str]:
        """
        Get list of all unique specializations.
        
        Returns:
            List of specializations
        """
        specializations = self.db.query(Doctor.specialization).distinct().all()
        return [s[0] for s in specializations if s[0]]
