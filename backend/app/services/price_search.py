"""
Price Search Service

Aggregates medicine prices from all pharmacy scrapers.
Provides price comparison, ranking, and savings calculation.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from app.services.scrapers import PharmEasyScraper, OneMgScraper, NetmedsScraper, ApolloScraper, TruemedsScraper, ScrapedPrice


class PriceSearchService:
    """Service for searching and comparing medicine prices across 5 pharmacies."""
    
    def __init__(self):
        self.scrapers = [
            PharmEasyScraper(),   # HTTP - Fast
            OneMgScraper(),       # Playwright - PRELOADED_STATE
            NetmedsScraper(),     # Playwright - __INITIAL_STATE__
            ApolloScraper(),      # Playwright - DOM
            TruemedsScraper()     # Playwright - DOM (best prices!)
        ]
    
    async def search_medicine(
        self, 
        medicine_name: str, 
        dosage: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for a medicine across all pharmacies.
        
        Args:
            medicine_name: Name of the medicine
            dosage: Optional dosage specification
        
        Returns:
            Dict with prices from all pharmacies, cheapest option, and savings
        """
        # Search all pharmacies - run in batches to avoid Playwright conflicts
        # PharmEasy uses HTTP (fast), others use Playwright
        all_prices = []
        pharmacy_results = {}
        errors = []
        
        # Batch 1: HTTP-based scrapers (fast)
        http_scrapers = [self.scrapers[0]]  # PharmEasy
        # Batch 2: Playwright-based scrapers (run in thread pools for uvicorn compatibility)
        playwright_scrapers = self.scrapers[1:]  # 1mg, Netmeds, Apollo, Truemeds
        
        # First, run HTTP scrapers
        for scraper in http_scrapers:
            try:
                result = await self._search_with_pharmacy(scraper, medicine_name, dosage)
                if result:
                    pharmacy_results[scraper.pharmacy_id] = result
                    all_prices.extend(result)
            except Exception as e:
                errors.append({"pharmacy": scraper.pharmacy_name, "error": str(e)})
        
        # Then run Playwright scrapers SEQUENTIALLY for maximum stability
        # Each uses asyncio.to_thread for uvicorn compatibility
        for scraper in playwright_scrapers:
            try:
                result = await self._search_with_pharmacy(scraper, medicine_name, dosage)
                if result:
                    pharmacy_results[scraper.pharmacy_id] = result
                    all_prices.extend(result)
            except Exception as e:
                errors.append({
                    "pharmacy": scraper.pharmacy_name,
                    "error": str(e)
                })
        
        # Find cheapest and calculate savings
        cheapest = None
        most_expensive = None
        savings = 0.0
        
        if all_prices:
            # Sort by price
            sorted_prices = sorted(all_prices, key=lambda x: x.price if x.price > 0 else float('inf'))
            valid_prices = [p for p in sorted_prices if p.price > 0]
            
            if valid_prices:
                cheapest = valid_prices[0]
                most_expensive = valid_prices[-1]
                savings = most_expensive.price - cheapest.price if len(valid_prices) > 1 else 0
        
        return {
            "success": True,
            "medicine_name": medicine_name,
            "dosage": dosage,
            "total_results": len(all_prices),
            "pharmacies_searched": [s.pharmacy_name for s in self.scrapers],
            "prices": [self._price_to_dict(p, s) for s, prices in pharmacy_results.items() for p in prices],
            "cheapest": self._price_to_dict(cheapest) if cheapest else None,
            "savings": round(savings, 2),
            "errors": errors if errors else None
        }
    
    async def _search_with_pharmacy(
        self, 
        scraper, 
        medicine_name: str, 
        dosage: Optional[str]
    ) -> List[ScrapedPrice]:
        """Search a single pharmacy with error handling."""
        try:
            return await scraper.search_with_retry(medicine_name, dosage)
        except Exception as e:
            print(f"Error searching {scraper.pharmacy_name}: {e}")
            return []
    
    def _price_to_dict(self, price: ScrapedPrice, pharmacy_id: str = None) -> Dict[str, Any]:
        """Convert ScrapedPrice to dictionary."""
        if not price:
            return None
        
        # Find pharmacy info
        pharmacy_name = "Unknown"
        for scraper in self.scrapers:
            if pharmacy_id and scraper.pharmacy_id == pharmacy_id:
                pharmacy_name = scraper.pharmacy_name
                break
            elif price.product_url:
                # Check all pharmacy URLs
                if "1mg" in price.product_url:
                    pharmacy_name = "1mg"
                elif "pharmeasy" in price.product_url:
                    pharmacy_name = "PharmEasy"
                elif "netmeds" in price.product_url:
                    pharmacy_name = "Netmeds"
                elif "apollopharmacy" in price.product_url:
                    pharmacy_name = "Apollo"
                elif "truemeds" in price.product_url:
                    pharmacy_name = "Truemeds"
        
        return {
            "pharmacy_id": pharmacy_id or pharmacy_name.lower().replace(" ", ""),
            "pharmacy_name": pharmacy_name,
            "product_name": price.product_name,
            "price": price.price,
            "original_price": price.original_price,
            "discount": price.discount,
            "pack_size": price.pack_size,
            "in_stock": price.in_stock,
            "delivery_days": price.delivery_days,
            "url": price.product_url,
            "image_url": price.image_url,
            "last_updated": datetime.now().isoformat()
        }
    
    async def search_multiple_medicines(
        self, 
        medicines: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Search prices for multiple medicines.
        
        Args:
            medicines: List of dicts with 'name' and 'dosage'
        
        Returns:
            Dict with results for each medicine and total savings
        """
        results = []
        total_savings = 0.0
        
        for medicine in medicines:
            name = medicine.get("name", "")
            dosage = medicine.get("dosage")
            
            if not name:
                continue
            
            result = await self.search_medicine(name, dosage)
            results.append(result)
            total_savings += result.get("savings", 0)
        
        return {
            "success": True,
            "medicines_count": len(results),
            "results": results,
            "total_savings": round(total_savings, 2)
        }
    
    async def close(self):
        """Close all scraper connections."""
        for scraper in self.scrapers:
            await scraper.close()


# Factory function - create fresh instance each time
async def get_price_search_service() -> PriceSearchService:
    """Create a new price search service instance."""
    # Always create fresh instance since scrapers manage their own browser instances
    return PriceSearchService()


async def search_medicine_prices(
    medicine_name: str,
    dosage: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to search medicine prices.
    
    Args:
        medicine_name: Name of the medicine
        dosage: Optional dosage specification
    
    Returns:
        Dict with prices and comparison data
    """
    service = await get_price_search_service()
    return await service.search_medicine(medicine_name, dosage)


async def search_multiple_medicines(medicines: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Convenience function to search multiple medicines.
    
    Args:
        medicines: List of medicine dicts
    
    Returns:
        Dict with all results
    """
    service = await get_price_search_service()
    return await service.search_multiple_medicines(medicines)
