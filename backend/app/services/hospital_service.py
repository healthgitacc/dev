"""
Hospital service for Super Owner management.
Handles hospital CRUD operations and status management.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Tuple
from datetime import datetime

from app.models import Hospital, HospitalStatus, User, UserRole
from app.core import NotFoundError, ValidationError, AppException


class HospitalService:
    """Service for managing hospitals (Super Owner only)."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_hospital(
        self,
        name: str,
        email: str,
        phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Hospital:
        """
        Create a new hospital.
        
        Args:
            name: Hospital name
            email: Hospital email
            phone: Hospital phone number
            address: Hospital address
            
        Returns:
            Created hospital
            
        Raises:
            ValidationError: If hospital name or email already exists
        """
        # Check if hospital name already exists
        existing_by_name = self.db.query(Hospital).filter(
            func.lower(Hospital.name) == func.lower(name)
        ).first()
        if existing_by_name:
            raise ValidationError("Hospital name already exists", field="name")
        
        # Check if hospital email already exists
        existing_by_email = self.db.query(Hospital).filter(
            func.lower(Hospital.email) == func.lower(email)
        ).first()
        if existing_by_email:
            raise ValidationError("Hospital email already exists", field="email")
        
        # Create hospital
        hospital = Hospital(
            name=name,
            email=email,
            phone=phone,
            address=address,
            status=HospitalStatus.INACTIVE,  # Start as inactive
        )
        
        self.db.add(hospital)
        self.db.commit()
        self.db.refresh(hospital)
        
        return hospital
    
    def get_hospital(self, hospital_id: int) -> Optional[Hospital]:
        """
        Get hospital by ID.
        
        Args:
            hospital_id: Hospital ID
            
        Returns:
            Hospital or None if not found
        """
        return self.db.query(Hospital).filter(Hospital.id == hospital_id).first()
    
    def get_all_hospitals(
        self,
        skip: int = 0,
        limit: int = 10,
        status_filter: Optional[HospitalStatus] = None,
    ) -> Tuple[List[dict], int]:
        """
        Get all hospitals with pagination and optional status filter.
        
        Args:
            skip: Records to skip
            limit: Records to return
            status_filter: Optional status filter
            
        Returns:
            Tuple of (hospitals_list, total_count)
        """
        query = self.db.query(Hospital)
        
        if status_filter:
            query = query.filter(Hospital.status == status_filter)
        
        query = query.order_by(Hospital.created_at.desc())
        total = query.count()
        hospitals = query.offset(skip).limit(limit).all()
        
        # Convert to dict format for API response
        hospital_list = [
            {
                "id": h.id,
                "name": h.name,
                "email": h.email,
                "phone": h.phone,
                "address": h.address,
                "status": h.status,
                "created_at": h.created_at.isoformat(),
                "updated_at": h.updated_at.isoformat(),
            }
            for h in hospitals
        ]
        
        return hospital_list, total
    
    def search_hospitals(
        self,
        query: str,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[dict], int]:
        """
        Search hospitals by name or email.
        
        Args:
            query: Search query
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (hospitals_list, total_count)
        """
        search_query = f"%{query.lower()}%"
        query_obj = self.db.query(Hospital).filter(
            (func.lower(Hospital.name).like(search_query)) |
            (func.lower(Hospital.email).like(search_query))
        ).order_by(Hospital.created_at.desc())
        
        total = query_obj.count()
        hospitals = query_obj.offset(skip).limit(limit).all()
        
        # Convert to dict format for API response
        hospital_list = [
            {
                "id": h.id,
                "name": h.name,
                "email": h.email,
                "phone": h.phone,
                "address": h.address,
                "status": h.status,
                "created_at": h.created_at.isoformat(),
                "updated_at": h.updated_at.isoformat(),
            }
            for h in hospitals
        ]
        
        return hospital_list, total
    
    def activate_hospital(self, hospital_id: int) -> Hospital:
        """
        Activate a hospital.
        
        Args:
            hospital_id: Hospital ID to activate
            
        Returns:
            Updated hospital
            
        Raises:
            NotFoundError: If hospital not found
        """
        hospital = self.get_hospital(hospital_id)
        if not hospital:
            raise NotFoundError("Hospital", hospital_id)
        
        hospital.status = HospitalStatus.ACTIVE
        hospital.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(hospital)
        
        return hospital
    
    def deactivate_hospital(self, hospital_id: int) -> Hospital:
        """
        Deactivate a hospital.
        
        Args:
            hospital_id: Hospital ID to deactivate
            
        Returns:
            Updated hospital
            
        Raises:
            NotFoundError: If hospital not found
        """
        hospital = self.get_hospital(hospital_id)
        if not hospital:
            raise NotFoundError("Hospital", hospital_id)
        
        hospital.status = HospitalStatus.INACTIVE
        hospital.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(hospital)
        
        return hospital
    
    def delete_hospital(self, hospital_id: int) -> None:
        """
        Delete a hospital and all associated users.
        
        Args:
            hospital_id: Hospital ID to delete
            
        Raises:
            NotFoundError: If hospital not found
        """
        hospital = self.get_hospital(hospital_id)
        if not hospital:
            raise NotFoundError("Hospital", hospital_id)
        from app.models import HospitalUser
        # Remove hospital-user assignments (cascade will handle this if configured)
        self.db.query(HospitalUser).filter(HospitalUser.hospital_id == hospital_id).delete()
        self.db.delete(hospital)
        self.db.commit()
    
    def get_hospital_with_users(self, hospital_id: int) -> Optional[dict]:
        """
        Get hospital details with associated users.
        Note: This is for Super Owner internal use only.
        
        Args:
            hospital_id: Hospital ID
            
        Returns:
            Hospital details with user count
        """
        hospital = self.get_hospital(hospital_id)
        if not hospital:
            return None
        from app.models import HospitalUser
        # Users linked to this hospital via HospitalUser (hospitals table is separate; link only here)
        user_ids = [hu.user_id for hu in self.db.query(HospitalUser).filter(HospitalUser.hospital_id == hospital_id).all()]
        user_counts = {}
        for role in [UserRole.HOSPITAL_ADMIN, UserRole.DOCTOR, UserRole.PATIENT]:
            if not user_ids:
                user_counts[role] = 0
            else:
                user_counts[role] = self.db.query(User).filter(
                    User.id.in_(user_ids),
                    User.role == role
                ).count()
        
        return {
            "id": hospital.id,
            "name": hospital.name,
            "email": hospital.email,
            "phone": hospital.phone,
            "address": hospital.address,
            "status": hospital.status,
            "user_counts": user_counts,
            "created_at": hospital.created_at.isoformat(),
            "updated_at": hospital.updated_at.isoformat(),
        }