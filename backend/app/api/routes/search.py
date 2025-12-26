"""
Search Routes

Handles medicine price search and comparison with history persistence.
Includes SSE streaming for progressive results.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
import json
import asyncio

from app.core.security import get_current_user_optional, OptionalUser, CurrentUser
from app.core.supabase import save_search_history, get_user_search_history, get_search_by_id
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
    search_id: Optional[str] = None


class SearchHistoryItem(BaseModel):
    """Search history entry."""
    id: str
    query: str
    medicines_count: int
    total_savings: float
    created_at: datetime


# ==============================================
# Search Endpoints
# ==============================================

@router.post("/medicine")
async def search_medicine(
    request: SearchRequest,
    current_user: OptionalUser = None
):
    """
    Search for a single medicine across all pharmacies.
    
    Returns prices from 1mg, PharmEasy, and Netmeds with:
    - Price comparison
    - Cheapest option highlighted
    - Potential savings calculated
    """
    search_id = f"search_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Search across all pharmacies
    result = await search_medicine_prices(request.medicine_name, request.dosage)
    
    # Save to history if user is authenticated
    if current_user and result.get("success"):
        try:
            saved = await save_search_history(
                user_id=current_user["id"],
                prescription_url=None,
                extracted_text=request.medicine_name,
                medicines=[{"name": request.medicine_name, "dosage": request.dosage}],
                results=result.get("prices", []),
                total_savings=result.get("savings", 0)
            )
            search_id = saved.get("id", search_id)
        except Exception as e:
            print(f"Failed to save search history: {e}")
    
    result["search_id"] = search_id
    return result


@router.post("/prescription/{prescription_id}")
async def search_prescription_medicines(
    prescription_id: str,
    current_user: OptionalUser = None
):
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
    
    # Save to history if user is authenticated
    search_id = f"search_{prescription_id}"
    if current_user and result.get("success"):
        try:
            saved = await save_search_history(
                user_id=current_user["id"],
                prescription_url=prescription.get("image_url"),
                extracted_text=prescription.get("extracted_text", ""),
                medicines=search_medicines,
                results=result.get("results", []),
                total_savings=result.get("total_savings", 0)
            )
            search_id = saved.get("id", search_id)
        except Exception as e:
            print(f"Failed to save search history: {e}")
    
    # Update prescription status
    prescription["status"] = "search_completed"
    prescription["search_results"] = result
    
    result["search_id"] = search_id
    result["prescription_id"] = prescription_id
    return result


@router.get("/history", response_model=List[SearchHistoryItem])
async def get_search_history(
    current_user: CurrentUser,
    limit: int = 10
):
    """
    Get user's search history.
    Requires authentication.
    """
    try:
        history = await get_user_search_history(current_user["id"], limit)
        
        items = []
        for item in history:
            medicines = item.get("medicines", [])
            query = ", ".join([m.get("name", "") for m in medicines]) if medicines else "Unknown"
            
            items.append(SearchHistoryItem(
                id=item["id"],
                query=query[:100],
                medicines_count=len(medicines),
                total_savings=float(item.get("total_savings", 0)),
                created_at=item.get("created_at", datetime.now())
            ))
        
        return items
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch search history: {str(e)}"
        )


@router.get("/history/{search_id}")
async def get_search_details(
    search_id: str,
    current_user: CurrentUser
):
    """
    Get details of a specific search.
    Requires authentication.
    """
    try:
        search = await get_search_by_id(search_id)
        
        if not search:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Search not found"
            )
        
        if search.get("user_id") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return {
            "success": True,
            "search": search
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch search details: {str(e)}"
        )
