"""
Search History API Routes

Endpoints for saving and retrieving user search history.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.supabase import get_supabase_client
from supabase import Client

router = APIRouter(prefix="/history", tags=["history"])


class SearchHistoryCreate(BaseModel):
    medicine_name: str
    search_type: str = "manual"  # 'prescription' or 'manual'
    results_count: int = 0
    cheapest_price: Optional[float] = None
    cheapest_pharmacy: Optional[str] = None
    prescription_image_url: Optional[str] = None


class SearchHistoryResponse(BaseModel):
    id: str
    user_id: str
    medicine_name: str
    search_type: str
    results_count: int
    cheapest_price: Optional[float]
    cheapest_pharmacy: Optional[str]
    prescription_image_url: Optional[str]
    created_at: str


@router.get("", response_model=List[SearchHistoryResponse])
async def get_search_history(
    limit: int = 50,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get user's search history.
    Requires authentication.
    """
    try:
        # Get current user
        user = supabase.auth.get_user()
        if not user or not user.user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Fetch search history
        response = (supabase.table("search_history")
            .select("*")
            .eq("user_id", user.user.id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute())
        
        return response.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")


@router.post("", response_model=SearchHistoryResponse)
async def save_search(
    search: SearchHistoryCreate,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Save a search to history.
    Requires authentication.
    """
    try:
        # Get current user
        user = supabase.auth.get_user()
        if not user or not user.user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Insert search history
        data = {
            "user_id": user.user.id,
            **search.dict()
        }
        
        response = (supabase.table("search_history")
            .insert(data)
            .execute())
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to save search")
        
        return response.data[0]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save search: {str(e)}")


@router.delete("/{search_id}")
async def delete_search(
    search_id: str,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Delete a search from history.
    Requires authentication.
    """
    try:
        # Get current user
        user = supabase.auth.get_user()
        if not user or not user.user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Delete search (RLS will ensure user owns it)
        response = (supabase.table("search_history")
            .delete()
            .eq("id", search_id)
            .eq("user_id", user.user.id)
            .execute())
        
        return {"success": True, "message": "Search deleted"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete search: {str(e)}")
