"""
Authentication Routes

Supabase authentication integration for user signup, login, and profile management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.supabase import (
    sign_up_user, 
    sign_in_user, 
    create_user_profile,
    get_user_profile,
    update_user_profile
)
from app.core.security import get_current_user, CurrentUser


router = APIRouter()


# ==============================================
# Request/Response Models
# ==============================================

class SignUpRequest(BaseModel):
    """Sign up request with email, password, and profile."""
    email: EmailStr
    password: str
    name: str
    location: str
    age: int
    sex: str


class SignInRequest(BaseModel):
    """Sign in request."""
    email: EmailStr
    password: str


class ProfileUpdateRequest(BaseModel):
    """Profile update request."""
    name: Optional[str] = None
    location: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None


class AuthResponse(BaseModel):
    """Authentication response."""
    success: bool
    message: str
    user: Optional[dict] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class ProfileResponse(BaseModel):
    """Profile response."""
    success: bool
    profile: Optional[dict] = None


# ==============================================
# Auth Endpoints
# ==============================================

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    """
    Register a new user with email and password.
    Also creates their profile.
    """
    try:
        # Sign up with Supabase Auth
        result = await sign_up_user(request.email, request.password)
        
        if not result.get("user"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        user = result["user"]
        session = result.get("session")
        
        # Create profile
        try:
            await create_user_profile(
                user_id=user["id"],
                name=request.name,
                email=request.email,
                location=request.location,
                age=request.age,
                sex=request.sex
            )
        except Exception as e:
            # Profile creation failed, but user was created
            print(f"Profile creation error: {e}")
        
        return AuthResponse(
            success=True,
            message="Account created successfully! Please check your email to verify.",
            user={
                "id": user["id"],
                "email": user["email"]
            },
            access_token=session.get("access_token") if session else None,
            refresh_token=session.get("refresh_token") if session else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: SignInRequest):
    """
    Login with email and password.
    """
    try:
        result = await sign_in_user(request.email, request.password)
        
        if not result.get("user") or not result.get("session"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user = result["user"]
        session = result["session"]
        
        # Get profile
        profile = await get_user_profile(user["id"])
        
        return AuthResponse(
            success=True,
            message="Login successful!",
            user={
                "id": user["id"],
                "email": user["email"],
                "profile": profile
            },
            access_token=session.get("access_token"),
            refresh_token=session.get("refresh_token")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(current_user: CurrentUser):
    """
    Get current user's profile.
    Requires authentication.
    """
    profile = await get_user_profile(current_user["id"])
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return ProfileResponse(
        success=True,
        profile=profile
    )


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: CurrentUser
):
    """
    Update current user's profile.
    Requires authentication.
    """
    # Build updates dict with only provided fields
    updates = {}
    if request.name is not None:
        updates["name"] = request.name
    if request.location is not None:
        updates["location"] = request.location
    if request.age is not None:
        updates["age"] = request.age
    if request.sex is not None:
        updates["sex"] = request.sex
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    profile = await update_user_profile(current_user["id"], updates)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return ProfileResponse(
        success=True,
        profile=profile
    )


@router.get("/me")
async def get_current_user_info(current_user: CurrentUser):
    """
    Get current authenticated user info.
    Useful for checking if token is valid.
    """
    profile = await get_user_profile(current_user["id"])
    
    return {
        "success": True,
        "user": {
            "id": current_user["id"],
            "email": current_user["email"],
            "profile": profile
        }
    }
