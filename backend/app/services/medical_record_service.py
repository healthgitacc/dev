"""
Medical Record service for medical record management.
Handles creation, updates, and queries of medical records.
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from app.models import MedicalRecord, Patient, Doctor
from app.services.base import BaseService
from app.core import (
    NotFoundError,
    ValidationError,
    paginate,
    get_logger,
)


logger = get_logger(__name__)


class MedicalRecordService(BaseService[MedicalRecord]):
    """Service for medical record management."""
    
    def __init__(self, db: Session):
        """
        Initialize medical record service.
        
        Args:
            db: Database session
        """
        super().__init__(db, MedicalRecord)
    
    def create_medical_record(
        self,
        patient_id: int,
        doctor_id: Optional[int],
        disease_name: str,
        diagnosis: str,
        prescription_text: Optional[str] = None,
        dosage: Optional[str] = None,
        follow_up_date: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> MedicalRecord:
        """
        Create a new medical record.
        
        Args:
            patient_id: Patient ID
            doctor_id: Doctor ID (who created the record)
            disease_name: Name of disease
            diagnosis: Diagnosis description
            prescription_text: Prescription text
            dosage: Medication dosage
            follow_up_date: Follow-up appointment date
            notes: Additional notes
            
        Returns:
            Created medical record
            
        Raises:
            NotFoundError: If patient or doctor not found
            ValidationError: If validation fails
        """
        # Verify patient exists
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise NotFoundError("Patient", patient_id)
        
        # Verify doctor if provided
        if doctor_id:
            doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
            if not doctor:
                raise NotFoundError("Doctor", doctor_id)
        
        # Validate follow-up date is in future
        if follow_up_date and follow_up_date <= datetime.utcnow():
            raise ValidationError("Follow-up date must be in the future", field="follow_up_date")
        
        try:
            record = MedicalRecord(
                patient_id=patient_id,
                doctor_id=doctor_id,
                disease_name=disease_name,
                diagnosis=diagnosis,
                prescription_text=prescription_text,
                dosage=dosage,
                follow_up_date=follow_up_date,
                notes=notes,
            )
            
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            
            logger.info(f"Medical record created: ID {record.id} for patient {patient_id}")
            
            return record
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating medical record: {str(e)}")
            raise
    
    def get_record_with_details(self, record_id: int) -> Optional[dict]:
        """
        Get medical record with doctor and patient details.
        
        Args:
            record_id: Record ID
            
        Returns:
            Dictionary with record and related info
        """
        record = self.get(record_id)
        if not record:
            return None
        
        return {
            "id": record.id,
            "patient_id": record.patient_id,
            "patient_name": record.patient.user.name,
            "doctor_id": record.doctor_id,
            "doctor_name": record.doctor.name if record.doctor else None,
            "doctor_specialization": record.doctor.specialization if record.doctor else None,
            "disease_name": record.disease_name,
            "diagnosis": record.diagnosis,
            "prescription_text": record.prescription_text,
            "dosage": record.dosage,
            "follow_up_date": record.follow_up_date,
            "notes": record.notes,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }
    
    def get_patient_records(
        self,
        patient_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[List[dict], int]:
        """
        Get all medical records for a patient.
        
        Args:
            patient_id: Patient ID
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (records, total_count)
        """
        # Verify patient exists
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise NotFoundError("Patient", patient_id)
        
        query = self.db.query(MedicalRecord).filter(
            MedicalRecord.patient_id == patient_id
        ).order_by(MedicalRecord.created_at.desc())
        
        records, total = paginate(query, skip, limit)
        
        result = []
        for record in records:
            result.append(self.get_record_with_details(record.id))
        
        return result, total
    
    def get_doctor_records(
        self,
        doctor_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[List[dict], int]:
        """
        Get all medical records created by a doctor.
        
        Args:
            doctor_id: Doctor ID
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (records, total_count)
        """
        # Verify doctor exists
        doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise NotFoundError("Doctor", doctor_id)
        
        query = self.db.query(MedicalRecord).filter(
            MedicalRecord.doctor_id == doctor_id
        ).order_by(MedicalRecord.created_at.desc())
        
        records, total = paginate(query, skip, limit)
        
        result = []
        for record in records:
            result.append(self.get_record_with_details(record.id))
        
        return result, total
    
    def get_all_records(
        self,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[List[dict], int]:
        """
        Get all medical records (admin only).
        
        Args:
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (records, total_count)
        """
        query = self.db.query(MedicalRecord).order_by(MedicalRecord.created_at.desc())
        
        records, total = paginate(query, skip, limit)
        
        result = []
        for record in records:
            result.append(self.get_record_with_details(record.id))
        
        return result, total

    def get_all_records_filtered(
        self,
        skip: int = 0,
        limit: int = 10,
        doctor_id: Optional[int] = None,
        patient_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> tuple[List[dict], int]:
        """
        Get all medical records with optional filters (admin only).
        
        Args:
            skip: Records to skip
            limit: Records to return
            doctor_id: Filter by doctor ID
            patient_id: Filter by patient ID
            date_from: Filter records created on or after this date
            date_to: Filter records created on or before this date
            
        Returns:
            Tuple of (records, total_count)
        """
        query = self.db.query(MedicalRecord)
        if doctor_id is not None:
            query = query.filter(MedicalRecord.doctor_id == doctor_id)
        if patient_id is not None:
            query = query.filter(MedicalRecord.patient_id == patient_id)
        if date_from is not None:
            query = query.filter(MedicalRecord.created_at >= date_from)
        if date_to is not None:
            query = query.filter(MedicalRecord.created_at <= date_to)
        query = query.order_by(MedicalRecord.created_at.desc())
        
        records, total = paginate(query, skip, limit)
        
        result = []
        for record in records:
            result.append(self.get_record_with_details(record.id))
        
        return result, total
    
    def get_follow_up_records(
        self,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[List[dict], int]:
        """
        Get medical records with upcoming follow-up appointments.
        
        Args:
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (records, total_count)
        """
        now = datetime.utcnow()
        
        query = self.db.query(MedicalRecord).filter(
            MedicalRecord.follow_up_date.isnot(None),
            MedicalRecord.follow_up_date >= now,
        ).order_by(MedicalRecord.follow_up_date)
        
        records, total = paginate(query, skip, limit)
        
        result = []
        for record in records:
            result.append(self.get_record_with_details(record.id))
        
        return result, total
    
    def get_records_by_disease(
        self,
        disease_name: str,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[List[dict], int]:
        """
        Get medical records by disease name.
        
        Args:
            disease_name: Disease name
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (records, total_count)
        """
        query = self.db.query(MedicalRecord).filter(
            MedicalRecord.disease_name.ilike(f"%{disease_name}%")
        ).order_by(MedicalRecord.created_at.desc())
        
        records, total = paginate(query, skip, limit)
        
        result = []
        for record in records:
            result.append(self.get_record_with_details(record.id))
        
        return result, total
    
    def update_medical_record(
        self,
        record_id: int,
        disease_name: Optional[str] = None,
        diagnosis: Optional[str] = None,
        prescription_text: Optional[str] = None,
        dosage: Optional[str] = None,
        follow_up_date: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> MedicalRecord:
        """
        Update medical record.
        
        Args:
            record_id: Record ID
            disease_name: Updated disease name
            diagnosis: Updated diagnosis
            prescription_text: Updated prescription
            dosage: Updated dosage
            follow_up_date: Updated follow-up date
            notes: Updated notes
            
        Returns:
            Updated medical record
            
        Raises:
            NotFoundError: If record not found
        """
        record = self.get(record_id)
        if not record:
            raise NotFoundError("MedicalRecord", record_id)
        
        update_data = {}
        if disease_name is not None:
            update_data["disease_name"] = disease_name
        if diagnosis is not None:
            update_data["diagnosis"] = diagnosis
        if prescription_text is not None:
            update_data["prescription_text"] = prescription_text
        if dosage is not None:
            update_data["dosage"] = dosage
        if follow_up_date is not None:
            if follow_up_date <= datetime.utcnow():
                raise ValidationError("Follow-up date must be in the future", field="follow_up_date")
            update_data["follow_up_date"] = follow_up_date
        if notes is not None:
            update_data["notes"] = notes
        
        if update_data:
            return super().update(record_id, update_data)
        
        return record
    
    def search_records(
        self,
        query_str: str,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[List[dict], int]:
        """
        Search medical records by disease name or diagnosis.
        
        Args:
            query_str: Search query
            skip: Records to skip
            limit: Records to return
            
        Returns:
            Tuple of (records, total_count)
        """
        search = f"%{query_str}%"
        query = self.db.query(MedicalRecord).filter(
            (MedicalRecord.disease_name.ilike(search)) |
            (MedicalRecord.diagnosis.ilike(search))
        )
        
        records, total = paginate(query, skip, limit)
        
        result = []
        for record in records:
            result.append(self.get_record_with_details(record.id))
        
        return result, total
