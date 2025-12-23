"""
Base Scraper

Abstract base class for pharmacy scrapers with common functionality.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import httpx
import asyncio
from bs4 import BeautifulSoup


class ScrapedPrice(BaseModel):
    """Scraped price data from a pharmacy."""
    product_name: str
    price: float
    original_price: Optional[float] = None
    discount: Optional[float] = None
    pack_size: str
    in_stock: bool = True
    delivery_days: Optional[int] = None
    product_url: str
    image_url: Optional[str] = None
    manufacturer: Optional[str] = None
    scraped_at: datetime = datetime.now()


class BaseScraper(ABC):
    """Abstract base class for pharmacy scrapers."""
    
    pharmacy_name: str = "Unknown"
    pharmacy_id: str = "unknown"
    base_url: str = ""
    search_url: str = ""
    
    # Common headers to mimic browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    
    def __init__(self):
        self.client = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if not self.client:
            self.client = httpx.AsyncClient(
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True
            )
        return self.client
    
    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
    
    @abstractmethod
    async def search(self, medicine_name: str, dosage: Optional[str] = None) -> List[ScrapedPrice]:
        """
        Search for a medicine on the pharmacy website.
        
        Args:
            medicine_name: Name of the medicine
            dosage: Optional dosage specification
        
        Returns:
            List of scraped prices
        """
        pass
    
    @abstractmethod
    async def get_product_details(self, product_url: str) -> Optional[ScrapedPrice]:
        """
        Get detailed information for a specific product.
        
        Args:
            product_url: URL of the product page
        
        Returns:
            ScrapedPrice with full details
        """
        pass
    
    def _build_search_url(self, query: str) -> str:
        """Build search URL for the pharmacy."""
        return f"{self.base_url}/search/all?name={query}"
    
    def _clean_price(self, price_str: str) -> float:
        """Clean price string and convert to float."""
        if not price_str:
            return 0.0
        # Remove currency symbols and commas
        cleaned = price_str.replace("₹", "").replace(",", "").replace("Rs.", "").replace("Rs", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def _calculate_discount(self, original: float, current: float) -> float:
        """Calculate discount percentage."""
        if original <= 0 or current <= 0:
            return 0.0
        return round(((original - current) / original) * 100, 1)
    
    async def health_check(self) -> bool:
        """Check if the pharmacy website is accessible."""
        try:
            client = await self._get_client()
            response = await client.get(self.base_url)
            return response.status_code == 200
        except Exception:
            return False
    
    async def search_with_retry(
        self, 
        medicine_name: str, 
        dosage: Optional[str] = None,
        max_retries: int = 3
    ) -> List[ScrapedPrice]:
        """
        Search with retry logic.
        
        Args:
            medicine_name: Name of the medicine
            dosage: Optional dosage
            max_retries: Maximum retry attempts
        
        Returns:
            List of scraped prices
        """
        for attempt in range(max_retries):
            try:
                results = await self.search(medicine_name, dosage)
                if results:
                    return results
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                    continue
                raise e
        return []
