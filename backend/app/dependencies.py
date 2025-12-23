"""
Shared dependencies for dependency injection.
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status

from app.config import Settings, get_settings


# Settings dependency
SettingsDep = Annotated[Settings, Depends(get_settings)]


def require_supabase_config(settings: SettingsDep) -> Settings:
    """Ensure Supabase is configured."""
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase is not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY."
        )
    return settings


def require_cloudinary_config(settings: SettingsDep) -> Settings:
    """Ensure Cloudinary is configured."""
    if not settings.cloudinary_cloud_name or not settings.cloudinary_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cloudinary is not configured. Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET."
        )
    return settings


def require_google_vision_config(settings: SettingsDep) -> Settings:
    """Ensure Google Cloud Vision is configured."""
    if not settings.google_application_credentials:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Cloud Vision is not configured. Please set GOOGLE_APPLICATION_CREDENTIALS."
        )
    return settings


def require_openai_config(settings: SettingsDep) -> Settings:
    """Ensure OpenAI is configured."""
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI is not configured. Please set OPENAI_API_KEY."
        )
    return settings
