"""
Prescription Routes

Handles prescription image upload, OCR, and medicine extraction.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.cloudinary import upload_prescription_image, get_optimized_url
from app.core.security import get_current_user_optional, get_current_user, OptionalUser, CurrentUser
from app.services.ocr import extract_text_from_url


router = APIRouter()


# ==============================================
# Models
# ==============================================

class Medicine(BaseModel):
    """Extracted medicine details."""
    id: str
    name: str
    generic_name: Optional[str] = None
    dosage: str
    frequency: Optional[str] = None
    quantity: Optional[int] = None
    is_generic: bool = False


class PrescriptionUploadResponse(BaseModel):
    """Response after uploading a prescription."""
    success: bool
    message: str
    prescription_id: str
    image_url: Optional[str] = None
    optimized_url: Optional[str] = None


class OCRResponse(BaseModel):
    """OCR extraction response."""
    success: bool
    prescription_id: str
    extracted_text: str
    confidence: float
    word_count: int = 0


class MedicineExtractionResponse(BaseModel):
    """Medicine extraction response."""
    success: bool
    prescription_id: str
    medicines: List[Medicine]
    raw_text: str


class ProcessingStatus(BaseModel):
    """Processing status response."""
    success: bool
    prescription_id: str
    status: str
    current_step: str
    steps: dict


# In-memory storage for prescription data (will be moved to DB later)
prescription_store = {}


# ==============================================
# Prescription Endpoints
# ==============================================

@router.post("/upload", response_model=PrescriptionUploadResponse)
async def upload_prescription(
    file: UploadFile = File(...),
    current_user: OptionalUser = None
):
    """
    Upload a prescription image to Cloudinary.
    
    Accepts: JPEG, PNG, WebP, PDF
    Returns: Cloudinary URL and prescription ID
    """
    # Validate file type
    allowed_types = [
        "image/jpeg", 
        "image/png", 
        "image/jpg", 
        "image/webp",
        "application/pdf"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{file.content_type}'. Allowed: JPEG, PNG, WebP, PDF"
        )
    
    # Validate file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10MB."
        )
    
    # Get user ID if authenticated
    user_id = current_user["id"] if current_user else None
    
    # Upload to Cloudinary
    result = await upload_prescription_image(
        file_bytes=contents,
        filename=file.filename or "prescription",
        user_id=user_id
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Failed to upload image")
        )
    
    # Generate prescription ID
    prescription_id = f"rx_{uuid.uuid4().hex[:12]}"
    
    # Get optimized URL for OCR
    optimized_url = None
    if result.get("public_id"):
        optimized_url = get_optimized_url(result["public_id"])
    
    # Store prescription data
    prescription_store[prescription_id] = {
        "id": prescription_id,
        "user_id": user_id,
        "image_url": result.get("secure_url"),
        "public_id": result.get("public_id"),
        "optimized_url": optimized_url,
        "status": "uploaded",
        "created_at": datetime.now().isoformat(),
        "extracted_text": None,
        "medicines": []
    }
    
    return PrescriptionUploadResponse(
        success=True,
        message="Prescription uploaded successfully!",
        prescription_id=prescription_id,
        image_url=result.get("secure_url"),
        optimized_url=optimized_url
    )


@router.get("/{prescription_id}")
async def get_prescription(prescription_id: str):
    """
    Get prescription details by ID.
    """
    if prescription_id not in prescription_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    return {
        "success": True,
        "prescription": prescription_store[prescription_id]
    }


@router.post("/{prescription_id}/ocr", response_model=OCRResponse)
async def extract_text(prescription_id: str):
    """
    Extract text from prescription image using Google Cloud Vision OCR.
    
    Uses the optimized Cloudinary URL for better OCR accuracy.
    """
    if prescription_id not in prescription_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    prescription = prescription_store[prescription_id]
    
    # Get the image URL (prefer optimized URL)
    image_url = prescription.get("optimized_url") or prescription.get("image_url")
    
    if not image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image URL found for this prescription"
        )
    
    # Call Google Cloud Vision OCR
    ocr_result = await extract_text_from_url(image_url)
    
    if not ocr_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ocr_result.get("error", "OCR extraction failed")
        )
    
    # Store extracted text in prescription
    extracted_text = ocr_result.get("text", "")
    prescription["extracted_text"] = extracted_text
    prescription["status"] = "ocr_completed"
    
    return OCRResponse(
        success=True,
        prescription_id=prescription_id,
        extracted_text=extracted_text,
        confidence=ocr_result.get("confidence", 0.0),
        word_count=ocr_result.get("word_count", 0)
    )


@router.post("/{prescription_id}/extract", response_model=MedicineExtractionResponse)
async def extract_medicines(prescription_id: str):
    """
    Extract medicine names and dosages using Gemini AI.
    
    Requires OCR to be run first (extracted_text must exist).
    """
    if prescription_id not in prescription_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    prescription = prescription_store[prescription_id]
    extracted_text = prescription.get("extracted_text")
    
    if not extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OCR has not been run yet. Call /ocr endpoint first."
        )
    
    # Import and call AI parser
    from app.services.ai_parser import extract_medicines_from_text
    
    ai_result = await extract_medicines_from_text(extracted_text)
    
    if not ai_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ai_result.get("error", "AI extraction failed")
        )
    
    # Convert to Medicine models with IDs
    medicines = []
    for i, med_data in enumerate(ai_result.get("medicines", [])):
        medicine = Medicine(
            id=f"med_{prescription_id}_{i}",
            name=med_data.get("name", ""),
            generic_name=med_data.get("generic_name"),
            dosage=med_data.get("dosage", ""),
            frequency=med_data.get("frequency"),
            quantity=med_data.get("quantity"),
            is_generic=med_data.get("is_generic", False)
        )
        medicines.append(medicine)
    
    # Store medicines in prescription
    prescription["medicines"] = [m.model_dump() for m in medicines]
    prescription["status"] = "extraction_completed"
    
    return MedicineExtractionResponse(
        success=True,
        prescription_id=prescription_id,
        medicines=medicines,
        raw_text=extracted_text
    )


@router.post("/{prescription_id}/process", response_model=ProcessingStatus)
async def process_prescription(prescription_id: str):
    """
    Full prescription processing pipeline.
    
    1. Verify image is uploaded
    2. OCR text extraction
    3. AI medicine extraction
    4. Return structured data
    """
    if prescription_id not in prescription_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    prescription = prescription_store[prescription_id]
    
    # Update status
    prescription["status"] = "processing"
    
    return ProcessingStatus(
        success=True,
        prescription_id=prescription_id,
        status="processing",
        current_step="upload",
        steps={
            "upload": "completed",
            "ocr": "pending",
            "extraction": "pending",
            "search": "pending"
        }
    )


@router.delete("/{prescription_id}")
async def delete_prescription(
    prescription_id: str,
    current_user: CurrentUser
):
    """
    Delete a prescription (requires authentication).
    """
    if prescription_id not in prescription_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    prescription = prescription_store[prescription_id]
    
    # Verify ownership
    if prescription.get("user_id") != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Delete from Cloudinary
    from app.core.cloudinary import delete_prescription_image
    if prescription.get("public_id"):
        await delete_prescription_image(prescription["public_id"])
    
    # Remove from store
    del prescription_store[prescription_id]
    
    return {"success": True, "message": "Prescription deleted"}
