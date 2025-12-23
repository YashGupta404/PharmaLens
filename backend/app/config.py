"""
PharmaLens Backend Configuration

Centralized configuration management using Pydantic Settings.
Loads environment variables from .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "PharmaLens API"
    app_version: str = "1.0.0"
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)
    
    # CORS - allow all common frontend ports
    cors_origins: str = Field(default="http://localhost:5173,http://localhost:3000,http://localhost:8080,http://localhost:8081,http://localhost:8000,http://127.0.0.1:8080,http://127.0.0.1:8081,http://127.0.0.1:5173")
    
    # Supabase
    supabase_url: str = Field(default="")
    supabase_anon_key: str = Field(default="")
    supabase_service_role_key: str = Field(default="")
    
    # Cloudinary
    cloudinary_cloud_name: str = Field(default="")
    cloudinary_api_key: str = Field(default="")
    cloudinary_api_secret: str = Field(default="")
    
    # Google Cloud Vision
    google_application_credentials: str = Field(default="")
    
    # Gemini AI (optional)
    gemini_api_key: str = Field(default="")
    
    # Groq AI (free alternative - uses Llama models)
    groq_api_key: str = Field(default="")
    
    # OpenAI (optional, kept for compatibility)
    openai_api_key: str = Field(default="")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"
    
    def validate_required_keys(self, *keys: str) -> dict:
        """
        Check which required keys are missing.
        Returns dict with key names and their status.
        """
        status = {}
        for key in keys:
            value = getattr(self, key, "")
            status[key] = bool(value and value != f"your_{key}")
        return status
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache for performance.
    """
    return Settings()


# Convenience function to get settings
settings = get_settings()
