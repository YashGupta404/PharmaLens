"""
Health Check Routes

Provides endpoints to verify API and service health.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any

from app.config import settings


router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    environment: str


class ServiceStatusResponse(BaseModel):
    """Detailed service status response."""
    status: str
    version: str
    environment: str
    services: Dict[str, Any]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    Returns API status and version.
    """
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.app_env
    )


@router.get("/health/services", response_model=ServiceStatusResponse)
async def service_status():
    """
    Detailed service status check.
    Shows configuration status for all external services.
    """
    services = {
        "supabase": {
            "configured": bool(settings.supabase_url and settings.supabase_anon_key),
            "url": settings.supabase_url[:30] + "..." if settings.supabase_url else None
        },
        "cloudinary": {
            "configured": bool(settings.cloudinary_cloud_name and settings.cloudinary_api_key),
            "cloud_name": settings.cloudinary_cloud_name or None
        },
        "google_vision": {
            "configured": bool(settings.google_application_credentials),
            "credentials_path": settings.google_application_credentials or None
        },
        "openai": {
            "configured": bool(settings.openai_api_key),
            "key_preview": settings.openai_api_key[:8] + "..." if settings.openai_api_key else None
        }
    }
    
    return ServiceStatusResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.app_env,
        services=services
    )


@router.get("/test-scrapers")
async def test_scrapers():
    """Test all scrapers to verify they work through uvicorn."""
    from app.services.scrapers import PharmEasyScraper, OneMgScraper, NetmedsScraper, ApolloScraper
    
    results = {}
    medicine = "Dolo 650"
    
    # Test each scraper sequentially
    scrapers = [
        ("PharmEasy", PharmEasyScraper()),
        ("1mg", OneMgScraper()),
        ("Netmeds", NetmedsScraper()),
        ("Apollo", ApolloScraper()),
    ]
    
    for name, scraper in scrapers:
        try:
            prices = await scraper.search(medicine)
            results[name] = {"count": len(prices), "status": "ok"}
            if prices:
                results[name]["first"] = prices[0].product_name[:40]
        except Exception as e:
            results[name] = {"count": 0, "status": "error", "error": str(e)}
        finally:
            try:
                await scraper.close()
            except:
                pass
    
    return {
        "medicine": medicine,
        "results": results,
        "total": sum(r["count"] for r in results.values())
    }
