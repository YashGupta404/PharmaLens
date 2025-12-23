"""
Security Utilities

JWT verification and auth helpers for Supabase.
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Annotated

from app.core.supabase import get_user_from_token, get_user_profile


security = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Verify JWT token from Supabase.
    Returns user data if valid, None if no token provided.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    user = await get_user_from_token(token)
    
    if user:
        return user
    
    return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    Get current authenticated user.
    Raises 401 if not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    user = await get_user_from_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Get current user if authenticated, None otherwise.
    Does not raise an error if not authenticated.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    user = await get_user_from_token(token)
    
    return user


async def get_current_user_with_profile(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    Get current user with their profile data.
    """
    user = await get_current_user(credentials)
    
    profile = await get_user_profile(user["id"])
    
    if profile:
        user["profile"] = profile
    
    return user


# Type aliases for dependency injection
CurrentUser = Annotated[dict, Depends(get_current_user)]
OptionalUser = Annotated[Optional[dict], Depends(get_current_user_optional)]
