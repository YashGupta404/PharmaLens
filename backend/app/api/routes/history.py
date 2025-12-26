"""
Search History API Routes

Endpoints for saving and retrieving user search history.
Updated to match existing Supabase table structure.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
from app.core.supabase import get_supabase_client
from supabase import Client

router = APIRouter(prefix="/history", tags=["history"])


class SearchHistoryCreate(BaseModel):
    prescription_url: Optional[str] = None
    extracted_text: Optional[str] = None
    medicines: List[dict] = []
    results: List[dict] = []
    total_savings: float = 0


class SearchHistoryResponse(BaseModel):
    id: str
    user_id: str
    prescription_url: Optional[str]
    extracted_text: Optional[str]
    medicines: List[dict]
    results: List[dict]
    total_savings: float
    created_at: str


@router.get("")
async def get_search_history(
    limit: int = 50,
    authorization: Optional[str] = Header(None)
):
    """
    Get user's search history.
    Requires authentication via Bearer token.
    """
    print(f"[History] GET request received")
    
    if not authorization or not authorization.startswith("Bearer "):
        print("[History] No auth token provided")
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    print(f"[History] Token received: {token[:20]}...")
    
    try:
        # Get supabase client with service role
        client = get_supabase_client()
        
        # Verify the token and get user
        user_response = client.auth.get_user(token)
        if not user_response or not user_response.user:
            print("[History] Invalid token - no user found")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user_response.user.id
        print(f"[History] User ID: {user_id}")
        
        # Fetch search history for this user
        response = (client.table("search_history")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute())
        
        print(f"[History] Found {len(response.data)} history items")
        return response.data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[History] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")


@router.post("")
async def save_search(
    search: SearchHistoryCreate,
    authorization: Optional[str] = Header(None)
):
    """
    Save a search to history.
    Requires authentication via Bearer token.
    """
    print(f"[History] POST request to save search")
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        client = get_supabase_client()
        
        # Verify token
        user_response = client.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user_response.user.id
        
        # Insert search history
        data = {
            "user_id": user_id,
            "prescription_url": search.prescription_url,
            "extracted_text": search.extracted_text,
            "medicines": search.medicines,
            "results": search.results,
            "total_savings": search.total_savings
        }
        
        response = client.table("search_history").insert(data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to save search")
        
        print(f"[History] Saved search for user {user_id}")
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[History] Save error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save search: {str(e)}")


@router.delete("/{search_id}")
async def delete_search(
    search_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Delete a search from history.
    Requires authentication via Bearer token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        client = get_supabase_client()
        
        # Verify token
        user_response = client.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user_response.user.id
        
        # Delete search (only if user owns it)
        response = (client.table("search_history")
            .delete()
            .eq("id", search_id)
            .eq("user_id", user_id)
            .execute())
        
        print(f"[History] Deleted search {search_id}")
        return {"success": True, "message": "Search deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[History] Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete search: {str(e)}")
