"""
User service for user management operations.
Handles CRUD operations for users with business logic.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import User, Doctor, Patient, UserRole, HospitalUser
from app.services.base import BaseService
from app.core import (
    NotFoundError,
    ConflictError,
    ValidationError,
    paginate,
    get_logger,
)
from app.schemas import UserCreate, UserResponse, UserUpdate, UserDetailResponse


logger = get_logger(__name__)


class UserService(BaseService[User]):
    """Service for user management."""
    
    def __init__(self, db: Session):
        """
        Initialize user service.
        
        Args:
            db: Database session
        """
        super().__init__(db, User)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email address
            
        Returns:
            User object or None
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_active_users(
        self,
        skip: int = 0,
        limit: int = 10,
        include_inactive: bool = False,
    ) -> tuple[List[User], int]:
        """
        Get users with pagination. By default only active; set include_inactive=True for all.
        """
        query = self.db.query(User)
        if not include_inactive:
            query = query.filter(User.is_active == True)
        return paginate(query, skip, limit)

    def get_users_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: int = 10,
        include_inactive: bool = False,
    ) -> tuple[List[User], int]:
        """
        Get users by role with pagination.
        """
        query = self.db.query(User).filter(User.role == role)
        if not include_inactive:
            query = query.filter(User.is_active == True)
        return paginate(query, skip, limit)
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user
            
        Raises:
            ConflictError: If email already exists
        """
        # Check if email exists
        if self.get_user_by_email(user_data.email):
            raise ConflictError(f"Email {user_data.email} already exists", field="email")
        
        from app.core import PasswordManager
        
        user_dict = user_data.dict()
        user_dict["password_hash"] = PasswordManager.hash_password(user_dict.pop("password"))
        
        return super().create(user_dict)
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        Update user information.
        
        Args:
            user_id: User ID
            user_data: Update data
            
        Returns:
            Updated user
            
        Raises:
            NotFoundError: If user not found
        """
        user = self.get(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        update_data = user_data.dict(exclude_unset=True)
        return super().update(user_id, update_data)
    
    def deactivate_user(self, user_id: int) -> User:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Deactivated user
            
        Raises:
            NotFoundError: If user not found
        """
        user = self.get(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        return super().update(user_id, {"is_active": False})
    
    def activate_user(self, user_id: int) -> User:
        """
        Activate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Activated user
            
        Raises:
            NotFoundError: If user not found
        """
        user = self.get(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        return super().update(user_id, {"is_active": True})
    
    def get_user_detail(self, user_id: int) -> Optional[UserDetailResponse]:
        """
        Get detailed user information including role-specific profile.
        
        Args:
            user_id: User ID
            
        Returns:
            Detailed user response
        """
        user = self.get(user_id)
        if not user:
            return None
        
        return UserDetailResponse.from_orm(user)
    
    def search_users(
        self,
        query: str,
        skip: int = 0,
        limit: int = 10,
        include_inactive: bool = False,
    ) -> tuple[List[User], int]:
        """
        Search users by name or email.
        """
        search = f"%{query}%"
        q = self.db.query(User).filter(
            (User.name.ilike(search)) | (User.email.ilike(search))
        )
        if not include_inactive:
            q = q.filter(User.is_active == True)
        return paginate(q, skip, limit)

    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user by id without loading relationships (avoids hospital_users
        lazy load when that table is missing). Deletes in order: hospital_users,
        doctor, patient, user.
        """
        from sqlalchemy import delete as sql_delete
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        try:
            self.db.execute(sql_delete(HospitalUser).where(HospitalUser.user_id == user_id))
        except Exception:
            self.db.rollback()
        try:
            self.db.query(Doctor).filter(Doctor.user_id == user_id).delete()
            self.db.query(Patient).filter(Patient.user_id == user_id).delete()
            self.db.query(User).filter(User.id == user_id).delete()
            self.db.commit()
            self.logger.info(f"Deleted User with id {user_id}")
            return True
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error deleting User with id {user_id}: {e}")
            raise
    
    def count_users_by_role(self) -> dict:
        """
        Get count of users by role.
        
        Returns:
            Dictionary with role counts
        """
        counts = {}
        for role in UserRole:
            count = self.db.query(User).filter(User.role == role).count()
            counts[role.value] = count
        
        return counts
