"""
Request/Response Schemas

API request and response models.
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============================================
# Auth Schemas
# ============================================

class UserProfileCreate(BaseModel):
    """User profile creation request."""
    name: str
    email: EmailStr
    location: str
    age: int
    sex: str


class UserProfileResponse(BaseModel):
    """User profile response."""
    id: str
    name: str
    email: str
    location: str
    age: int
    sex: str
    created_at: datetime


class AuthResponse(BaseModel):
    """Generic auth response."""
    success: bool
    message: str
    user: Optional[UserProfileResponse] = None
    access_token: Optional[str] = None


# ============================================
# Prescription Schemas
# ============================================

class PrescriptionUploadResponse(BaseModel):
    """Response after uploading prescription."""
    success: bool
    message: str
    prescription_id: str
    image_url: Optional[str] = None


class OCRResult(BaseModel):
    """OCR extraction result."""
    success: bool
    prescription_id: str
    extracted_text: str
    confidence: float


class ExtractedMedicine(BaseModel):
    """Single extracted medicine."""
    name: str
    dosage: str
    frequency: Optional[str] = None
    quantity: Optional[int] = None


class MedicineExtractionResult(BaseModel):
    """Medicine extraction result."""
    success: bool
    prescription_id: str
    medicines: List[ExtractedMedicine]
    raw_text: str


# ============================================
# Search Schemas
# ============================================

class MedicineSearchRequest(BaseModel):
    """Medicine search request."""
    medicine_name: str
    dosage: Optional[str] = None


class PharmacyPriceSchema(BaseModel):
    """Pharmacy price in response."""
    pharmacy_id: str
    pharmacy_name: str
    pharmacy_logo: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    discount: Optional[float] = None
    pack_size: str
    in_stock: bool
    delivery_days: Optional[int] = None
    url: str
    last_updated: datetime


class GenericAlternativeSchema(BaseModel):
    """Generic alternative in response."""
    id: str
    name: str
    composition: str
    price_range: Dict[str, float]  # {"min": x, "max": y}
    pharmacies_count: int


class MedicineResultSchema(BaseModel):
    """Single medicine result."""
    medicine_name: str
    generic_name: Optional[str] = None
    dosage: str
    prices: List[PharmacyPriceSchema]
    cheapest_price: Optional[PharmacyPriceSchema] = None
    generic_alternatives: List[GenericAlternativeSchema] = []
    savings: Optional[float] = None


class SearchResponse(BaseModel):
    """Complete search response."""
    success: bool
    search_id: str
    results: List[MedicineResultSchema]
    total_savings: float
    medicines_count: int
    pharmacies_searched: List[str]


class SearchHistorySchema(BaseModel):
    """Search history entry."""
    id: str
    query: str
    medicines_count: int
    total_savings: float
    created_at: datetime


# ============================================
# Error Schemas
# ============================================

class ErrorResponse(BaseModel):
    """Error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
