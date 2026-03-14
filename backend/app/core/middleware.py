"""
Middleware for access control and role-based restrictions.
Provides middleware functions to enforce Super Owner access control policies.
"""
from fastapi import Request, HTTPException, status
from typing import Callable, Awaitable
from app.models import UserRole


async def super_owner_access_control_middleware(
    request: Request, 
    call_next: Callable[[Request], Awaitable]
) -> Awaitable:
    """
    Middleware to enforce Super Owner access control.
    
    Blocks Super Owner from accessing patient, doctor, appointment, and medical record endpoints.
    Super Owner can only access hospital management endpoints.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware or route handler
        
    Returns:
        Response from next handler or raises HTTPException
        
    Raises:
        403 Forbidden: If Super Owner tries to access restricted endpoints
    """
    # Get user from request state (set by authentication middleware)
    current_user = getattr(request.state, 'current_user', None)
    
    if current_user and current_user.role == UserRole.SUPER_OWNER:
        # Define restricted paths that Super Owner cannot access
        restricted_paths = [
            '/patients',
            '/doctors', 
            '/appointments',
            '/medical-records'
        ]
        
        # Check if the current path matches any restricted path
        current_path = request.url.path
        
        # Check for exact matches or paths that start with restricted prefixes
        for restricted_path in restricted_paths:
            if current_path.startswith(restricted_path):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "message": "Super Owner access restricted",
                        "code": "SUPER_OWNER_ACCESS_DENIED",
                        "allowed_endpoints": [
                            "/admin/hospitals",
                            "/admin/hospitals/{id}",
                            "/auth/register",
                            "/auth/login"
                        ],
                        "restricted_endpoints": [
                            "/patients/*",
                            "/doctors/*", 
                            "/appointments/*",
                            "/medical-records/*"
                        ]
                    }
                )
    
    # Continue to next middleware/route handler
    response = await call_next(request)
    return response


async def hospital_admin_data_isolation_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable]
) -> Awaitable:
    """
    Middleware to enforce hospital_admin data isolation.
    
    Ensures hospital_admin can only access their own hospital's data.
    This is a placeholder for future hospital_id-based isolation.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware or route handler
        
    Returns:
        Response from next handler
    """
    # Get user from request state
    current_user = getattr(request.state, 'current_user', None)
    
    if current_user and current_user.role == UserRole.HOSPITAL_ADMIN:
        # TODO: Implement hospital_id-based data isolation
        # For now, this middleware is a placeholder for future implementation
        # where we would check hospital_id in requests and filter data accordingly
        pass
    
    response = await call_next(request)
    return response


def create_super_owner_guard():
    """
    Create a dependency guard for Super Owner role.
    
    Use this as a dependency in routes that should only be accessible by Super Owner.
    
    Returns:
        Dependency function that validates Super Owner role
    """
    def guard(current_user: any = None) -> None:  # 'any' to avoid circular import
        """
        Guard function to validate Super Owner role.
        
        Args:
            current_user: Current authenticated user
            
        Raises:
            HTTPException: If user is not Super Owner
        """
        if not current_user or current_user.role != UserRole.SUPER_OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Super Owner access required",
                    "code": "SUPER_OWNER_REQUIRED"
                }
            )
    
    return guard


def create_hospital_admin_guard():
    """
    Create a dependency guard for Hospital Admin role.
    
    Use this as a dependency in routes that should only be accessible by Hospital Admin.
    
    Returns:
        Dependency function that validates Hospital Admin role
    """
    def guard(current_user: any = None) -> None:  # 'any' to avoid circular import
        """
        Guard function to validate Hospital Admin role.
        
        Args:
            current_user: Current authenticated user
            
        Raises:
            HTTPException: If user is not Hospital Admin
        """
        if not current_user or current_user.role != UserRole.HOSPITAL_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Hospital Admin access required",
                    "code": "HOSPITAL_ADMIN_REQUIRED"
                }
            )
    
    return guard