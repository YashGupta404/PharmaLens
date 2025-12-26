"""
Search Routes - NO HISTORY VERSION

Handles medicine price search and comparison.
Search history has been removed to reduce complexity.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

from app.services.price_search import search_medicine_prices, search_multiple_medicines


router = APIRouter()


# ==============================================
# Models
# ==============================================

class PharmacyPriceResponse(BaseModel):
    """Price from a pharmacy."""
    pharmacy_id: str
    pharmacy_name: str
    product_name: str
    price: float
    original_price: Optional[float] = None
    discount: Optional[float] = None
    pack_size: str
    in_stock: bool
    delivery_days: Optional[int] = None
    url: str
    image_url: Optional[str] = None
    last_updated: str


class SearchRequest(BaseModel):
    """Medicine search request."""
    medicine_name: str
    dosage: Optional[str] = None


class SingleMedicineResponse(BaseModel):
    """Response for single medicine search."""
    success: bool
    medicine_name: str
    dosage: Optional[str]
    total_results: int
    pharmacies_searched: List[str]
    prices: List[Any]
    cheapest: Optional[Any]
    savings: float


# ==============================================
# Search Endpoints
# ==============================================

@router.post("/medicine")
async def search_medicine(request: SearchRequest):
    """
    Search for a single medicine across all pharmacies.
    
    Returns prices from PharmEasy, 1mg, Netmeds, Apollo with:
    - Price comparison
    - Cheapest option highlighted
    - Potential savings calculated
    
    Average search time: 10-20 seconds
    """
    print(f"\n[API] Search request: {request.medicine_name}")
    
    # Search across all pharmacies
    result = await search_medicine_prices(request.medicine_name, request.dosage)
    
    # Generate a simple search ID (no database storage)
    result["search_id"] = f"search_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return result


@router.post("/prescription/{prescription_id}")
async def search_prescription_medicines(prescription_id: str):
    """
    Search for all medicines from a prescription.
    
    1. Get extracted medicines from prescription store
    2. Search each medicine across pharmacies
    3. Aggregate and return results with total savings
    """
    # Import prescription store
    from app.api.routes.prescriptions import prescription_store
    
    if prescription_id not in prescription_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    prescription = prescription_store[prescription_id]
    medicines = prescription.get("medicines", [])
    
    if not medicines:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No medicines extracted. Run /extract endpoint first."
        )
    
    # Convert medicines to search format
    search_medicines = [
        {"name": m.get("name", ""), "dosage": m.get("dosage", "")}
        for m in medicines
        if m.get("name")
    ]
    
    # Search all medicines
    result = await search_multiple_medicines(search_medicines)
    
    # Update prescription status
    prescription["status"] = "search_completed"
    prescription["search_results"] = result
    
    result["search_id"] = f"search_{prescription_id}"
    result["prescription_id"] = prescription_id
    return result
