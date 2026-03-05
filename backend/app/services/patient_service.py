"""
Patient service for patient-specific operations.
Handles patient profile management and patient-related queries.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import Patient, User, Gender, BloodGroup
from app.services.base import BaseService
from app.core import (
    NotFoundError,
    ValidationError,
    paginate,
    get_logger,
)


logger = get_logger(__name__)


class PatientService(BaseService[Patient]):
    """Service for patient management."""
    
    def __init__(self, db: Session):
        """
        Initialize patient service.
        
        Args:
            db: Database session
        """
        super().__init__(db, Patient)
    
    def get_patient_by_user_id(self, user_id: int) -> Optional[Patient]:
        """
        Get patient by user ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Patient object or None
        """
        return self.db.query(Patient).filter(Patient.user_id == user_id).first()
    
    def get_patient_with_user(self, patient_id: int) -> Optional[dict]:
        """
        Get patient with associated user information.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Dictionary with patient and user info
        """
        patient = self.get(patient_id)
        if not patient:
            return None
        
        return {
            "id": patient.id,
            "user_id": patient.user_id,
            "name": patient.user.name,
            "email": patient.user.email,
            "phone": patient.user.phone,
            "age": patient.age,
            "gender": patient.gender if patient.gender else None,
            "blood_group": patient.blood_group if patient.blood_group else None,
            "medical_history": patient.medical_history,
            "is_active": patient.user.is_active,
            "created_at": patient.created_at,
        }
    
    def create_patient(
        self,
        user_id: int,
        blood_group: Optional[str] = None,
        gender: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        address: Optional[str] = None,
        medical_history: Optional[str] = None,
    ) -> Patient:
        """
        Create a new patient profile for a registered user.
        
        Args:
            user_id: User ID
            blood_group: Patient blood group
            gender: Patient gender
            date_of_birth: Date of birth
            address: Patient address
            medical_history: Medical history
            
        Returns:
            Created patient object
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if patient already exists
        existing = self.db.query(Patient).filter(Patient.user_id == user_id).first()
        if existing:
            raise ValidationError(f"Patient profile already exists for user {user_id}", field="user_id")
        
        patient = Patient(
            user_id=user_id,
            blood_group=blood_group,
            gender=gender,
            address=address,
            medical_history=medical_history,
        )
        
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        
        logger.info(f"Patient profile created for user {user_id}")
        return patient
    
    def get_all_patients(self, skip: int = 0, limit: int = 10) -> tuple[List[dict], int]:
        """
        Get all active patients.
        
        Args:
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (patients, total_count)
        """
        query = self.db.query(Patient).join(User).filter(User.is_active == True)
        patients, total = paginate(query, skip, limit)
        
        result = []
        for patient in patients:
            result.append(self.get_patient_with_user(patient.id))
        
        return result, total
    
    def update_patient_profile(
        self,
        patient_id: int,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        blood_group: Optional[str] = None,
        medical_history: Optional[str] = None,
    ) -> Optional[Patient]:
        """
        Update patient profile information.
        
        Args:
            patient_id: Patient ID
            age: Patient age
            gender: Patient gender (male/female/other)
            blood_group: Patient blood group
            medical_history: Medical history
            
        Returns:
            Updated patient object
            
        Raises:
            NotFoundError: If patient not found
            ValidationError: If validation fails
        """
        patient = self.get(patient_id)
        if not patient:
            raise NotFoundError("Patient", patient_id)
        
        # Validate age
        if age is not None:
            if age < 0 or age > 150:
                raise ValidationError("Age must be between 0 and 150", field="age")
        
        # Validate gender
        if gender is not None:
            try:
                Gender(gender)
            except ValueError:
                valid_genders = [g.value for g in Gender]
                raise ValidationError(
                    f"Gender must be one of {valid_genders}",
                    field="gender"
                )
        
        # Validate blood group
        if blood_group is not None:
            try:
                BloodGroup(blood_group)
            except ValueError:
                valid_groups = [b.value for b in BloodGroup]
                raise ValidationError(
                    f"Blood group must be one of {valid_groups}",
                    field="blood_group"
                )
        
        update_data = {}
        if age is not None:
            update_data["age"] = age
        if gender is not None:
            update_data["gender"] = gender
        if blood_group is not None:
            update_data["blood_group"] = blood_group
        if medical_history is not None:
            update_data["medical_history"] = medical_history
        
        if update_data:
            return super().update(patient_id, update_data)
        
        return patient
    
    def get_patients_by_blood_group(
        self,
        blood_group: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[dict], int]:
        """
        Get patients by blood group.
        
        Args:
            blood_group: Blood group
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (patients, total_count)
        """
        try:
            BloodGroup(blood_group)
        except ValueError:
            raise ValidationError(f"Invalid blood group: {blood_group}", field="blood_group")
        
        query = self.db.query(Patient).filter(Patient.blood_group == blood_group)
        patients, total = paginate(query, skip, limit)
        
        result = []
        for patient in patients:
            result.append(self.get_patient_with_user(patient.id))
        
        return result, total
    
    def get_patients_by_gender(
        self,
        gender: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[dict], int]:
        """
        Get patients by gender.
        
        Args:
            gender: Gender (male/female/other)
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (patients, total_count)
        """
        try:
            Gender(gender)
        except ValueError:
            raise ValidationError(f"Invalid gender: {gender}", field="gender")
        
        query = self.db.query(Patient).filter(Patient.gender == gender)
        patients, total = paginate(query, skip, limit)
        
        result = []
        for patient in patients:
            result.append(self.get_patient_with_user(patient.id))
        
        return result, total
    
    def search_patients(
        self,
        query: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[dict], int]:
        """
        Search patients by name or email.
        
        Args:
            query: Search query
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (patients, total_count)
        """
        search = f"%{query}%"
        q = self.db.query(Patient).join(User).filter(
            (User.name.ilike(search)) | (User.email.ilike(search))
        )
        patients, total = paginate(q, skip, limit)
        
        result = []
        for patient in patients:
            result.append(self.get_patient_with_user(patient.id))
        
        return result, total
