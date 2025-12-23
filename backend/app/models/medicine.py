"""
Medicine Models

Pydantic models for medicine data.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Medicine(BaseModel):
    """Medicine details."""
    id: str
    name: str
    generic_name: Optional[str] = None
    dosage: str
    frequency: Optional[str] = None
    quantity: Optional[int] = None
    is_generic: bool = False


class PharmacyPrice(BaseModel):
    """Price from a pharmacy."""
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
    last_updated: datetime = datetime.now()


class GenericAlternative(BaseModel):
    """Generic alternative medicine."""
    id: str
    name: str
    composition: str
    price_range_min: float
    price_range_max: float
    pharmacies_count: int


class MedicineSearchResult(BaseModel):
    """Complete search result for a medicine."""
    medicine: Medicine
    prices: List[PharmacyPrice]
    cheapest_price: Optional[PharmacyPrice] = None
    generic_alternatives: List[GenericAlternative] = []
    savings: Optional[float] = None


class PrescriptionScan(BaseModel):
    """Prescription scan record."""
    id: str
    user_id: str
    image_url: str
    extracted_text: str
    medicines: List[Medicine]
    status: str  # uploading, processing, extracting, searching, completed, error
    created_at: datetime = datetime.now()
    results: Optional[List[MedicineSearchResult]] = None


class SearchHistory(BaseModel):
    """User search history entry."""
    id: str
    user_id: str
    query: str
    medicines_count: int
    total_savings: float
    created_at: datetime
    prescription_scan_id: Optional[str] = None
