"""
Cloudinary Client

Handles image uploads to Cloudinary for prescription images.
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional, Dict, Any
from datetime import datetime

from app.config import settings


def configure_cloudinary():
    """
    Configure Cloudinary SDK with credentials from environment.
    Must be called before any upload operations.
    """
    if not settings.cloudinary_cloud_name:
        raise ValueError("CLOUDINARY_CLOUD_NAME not configured in .env")
    
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )


def _ensure_configured():
    """Ensure Cloudinary is configured before operations."""
    if not cloudinary.config().cloud_name:
        configure_cloudinary()


async def upload_prescription_image(
    file_bytes: bytes,
    filename: str,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload prescription image to Cloudinary.
    
    Args:
        file_bytes: Image file bytes
        filename: Original filename
        user_id: Optional user ID for folder organization
    
    Returns:
        dict with:
        - secure_url: HTTPS URL for the image
        - public_id: Cloudinary public ID
        - width, height: Image dimensions
        - format: Image format (jpg, png, etc.)
        - created_at: Upload timestamp
    """
    _ensure_configured()
    
    # Generate unique public ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = filename.rsplit(".", 1)[0].replace(" ", "_")[:30]
    
    # Organize by user if provided
    folder = f"pharmalens/prescriptions/{user_id}" if user_id else "pharmalens/prescriptions"
    public_id = f"{folder}/{safe_filename}_{timestamp}"
    
    try:
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file_bytes,
            public_id=public_id,
            folder=None,  # Already included in public_id
            resource_type="image",
            # Optimize for OCR
            transformation=[
                {"quality": "auto:best"},
                {"fetch_format": "auto"}
            ],
            # Add tags for organization
            tags=["prescription", "pharmalens"],
            # Context metadata
            context={
                "original_filename": filename,
                "uploaded_at": timestamp
            }
        )
        
        return {
            "success": True,
            "secure_url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "width": result.get("width"),
            "height": result.get("height"),
            "format": result.get("format"),
            "bytes": result.get("bytes"),
            "created_at": result.get("created_at"),
            "original_filename": filename
        }
        
    except cloudinary.exceptions.Error as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to upload image to Cloudinary"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Unexpected error during upload"
        }


async def delete_prescription_image(public_id: str) -> bool:
    """
    Delete an image from Cloudinary.
    
    Args:
        public_id: Cloudinary public ID of the image
    
    Returns:
        True if deleted successfully, False otherwise
    """
    _ensure_configured()
    
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception:
        return False


async def get_image_info(public_id: str) -> Optional[Dict[str, Any]]:
    """
    Get information about an uploaded image.
    
    Args:
        public_id: Cloudinary public ID
    
    Returns:
        Image info dict or None if not found
    """
    _ensure_configured()
    
    try:
        result = cloudinary.api.resource(public_id)
        return {
            "public_id": result.get("public_id"),
            "secure_url": result.get("secure_url"),
            "width": result.get("width"),
            "height": result.get("height"),
            "format": result.get("format"),
            "bytes": result.get("bytes"),
            "created_at": result.get("created_at")
        }
    except cloudinary.exceptions.NotFound:
        return None
    except Exception:
        return None


def get_optimized_url(public_id: str, width: int = 1200) -> str:
    """
    Get an optimized URL for OCR processing.
    
    Args:
        public_id: Cloudinary public ID
        width: Max width for the image
    
    Returns:
        Optimized image URL
    """
    _ensure_configured()
    
    # Build URL with transformations optimized for OCR
    url, _ = cloudinary.utils.cloudinary_url(
        public_id,
        transformation=[
            {"width": width, "crop": "limit"},
            {"quality": "auto:best"},
            {"fetch_format": "png"}  # PNG for better OCR
        ]
    )
    
    return url
