"""
Supabase Client

Handles Supabase connection for authentication and database operations.
"""

from supabase import create_client, Client
from typing import Optional, Dict, Any, List
from functools import lru_cache

from app.config import settings


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get cached Supabase client instance.
    Uses service role key for backend operations.
    """
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise ValueError(
            "Supabase credentials not configured. "
            "Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env"
        )
    
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )


def get_supabase_anon_client() -> Client:
    """
    Get Supabase client with anon key.
    Used for client-side operations.
    """
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise ValueError(
            "Supabase credentials not configured. "
            "Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env"
        )
    
    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key
    )


# ==============================================
# User Profile Operations
# ==============================================

async def create_user_profile(
    user_id: str,
    name: str,
    email: str,
    location: str,
    age: int,
    sex: str
) -> Dict[str, Any]:
    """
    Create a new user profile.
    """
    client = get_supabase_client()
    
    data = {
        "id": user_id,
        "name": name,
        "email": email,
        "location": location,
        "age": age,
        "sex": sex
    }
    
    result = client.table("profiles").insert(data).execute()
    
    if result.data:
        return result.data[0]
    return {}


async def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get user profile by ID.
    """
    client = get_supabase_client()
    
    result = client.table("profiles").select("*").eq("id", user_id).execute()
    
    if result.data and len(result.data) > 0:
        return result.data[0]
    return None


async def update_user_profile(
    user_id: str,
    updates: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update user profile.
    """
    client = get_supabase_client()
    
    result = client.table("profiles").update(updates).eq("id", user_id).execute()
    
    if result.data and len(result.data) > 0:
        return result.data[0]
    return None


# ==============================================
# Search History Operations
# ==============================================

async def save_search_history(
    user_id: str,
    prescription_url: Optional[str],
    extracted_text: str,
    medicines: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    total_savings: float
) -> Dict[str, Any]:
    """
    Save a search to history.
    """
    client = get_supabase_client()
    
    data = {
        "user_id": user_id,
        "prescription_url": prescription_url,
        "extracted_text": extracted_text,
        "medicines": medicines,
        "results": results,
        "total_savings": total_savings
    }
    
    result = client.table("search_history").insert(data).execute()
    
    if result.data:
        return result.data[0]
    return {}


async def get_user_search_history(
    user_id: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get user's search history.
    """
    client = get_supabase_client()
    
    result = (
        client.table("search_history")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    
    return result.data if result.data else []


async def get_search_by_id(search_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific search by ID.
    """
    client = get_supabase_client()
    
    result = client.table("search_history").select("*").eq("id", search_id).execute()
    
    if result.data and len(result.data) > 0:
        return result.data[0]
    return None


# ==============================================
# Auth Operations (using Supabase Auth)
# ==============================================

async def sign_up_user(email: str, password: str) -> Dict[str, Any]:
    """
    Sign up a new user with email and password.
    """
    client = get_supabase_anon_client()
    
    result = client.auth.sign_up({
        "email": email,
        "password": password
    })
    
    return {
        "user": result.user.__dict__ if result.user else None,
        "session": result.session.__dict__ if result.session else None
    }


async def sign_in_user(email: str, password: str) -> Dict[str, Any]:
    """
    Sign in a user with email and password.
    """
    client = get_supabase_anon_client()
    
    result = client.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    
    return {
        "user": result.user.__dict__ if result.user else None,
        "session": result.session.__dict__ if result.session else None
    }


async def sign_out_user(access_token: str) -> bool:
    """
    Sign out a user.
    """
    client = get_supabase_client()
    
    try:
        client.auth.sign_out()
        return True
    except Exception:
        return False


async def get_user_from_token(access_token: str) -> Optional[Dict[str, Any]]:
    """
    Get user from JWT access token.
    """
    client = get_supabase_client()
    
    try:
        result = client.auth.get_user(access_token)
        if result and result.user:
            return {
                "id": result.user.id,
                "email": result.user.email,
                "created_at": str(result.user.created_at)
            }
    except Exception:
        pass
    
    return None
