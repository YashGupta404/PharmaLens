"""
Price Search Service - SIMPLE VERSION

Direct pharmacy scraping without streaming (more reliable on Render).
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from app.services.scrapers import PharmEasyScraper, OneMgScraper, NetmedsScraper, ApolloScraper, ScrapedPrice


class PriceSearchService:
    """Service for searching and comparing medicine prices across 4 pharmacies."""
    
    def __init__(self):
        print("[PriceSearch] Initializing scrapers...")
        self.scrapers = [
            PharmEasyScraper(),   # HTTP - Fast
            OneMgScraper(),       # Playwright
            NetmedsScraper(),     # Playwright
            ApolloScraper(),      # Playwright
        ]
        print(f"[PriceSearch] Initialized {len(self.scrapers)} scrapers")
    
    async def search_medicine(
        self, 
        medicine_name: str, 
        dosage: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for a medicine across all pharmacies.
        SEQUENTIAL execution to save memory on Render.
        """
        print(f"\n{'='*50}")
        print(f"[PriceSearch] Starting search for: {medicine_name}")
        print(f"{'='*50}")
        
        all_prices = []
        pharmacy_results = {}
        errors = []
        
        for i, scraper in enumerate(self.scrapers):
            pharmacy_name = scraper.pharmacy_name
            print(f"\n[{i+1}/{len(self.scrapers)}] Searching {pharmacy_name}...")
            
            try:
                # 60 second timeout per pharmacy
                result = await asyncio.wait_for(
                    self._search_with_pharmacy(scraper, medicine_name, dosage),
                    timeout=60.0
                )
                
                count = len(result) if result else 0
                print(f"[{pharmacy_name}] ✅ Found {count} results")
                
                if result:
                    pharmacy_results[scraper.pharmacy_id] = result
                    all_prices.extend(result)
                    
            except asyncio.TimeoutError:
                print(f"[{pharmacy_name}] ⚠️ TIMEOUT after 60s")
                errors.append({"pharmacy": pharmacy_name, "error": "Timeout"})
                
            except Exception as e:
                print(f"[{pharmacy_name}] ❌ ERROR: {str(e)[:100]}")
                errors.append({"pharmacy": pharmacy_name, "error": str(e)})
        
        # Calculate results
        print(f"\n[PriceSearch] Search complete. Total results: {len(all_prices)}")
        
        cheapest = None
        most_expensive = None
        savings = 0.0
        
        if all_prices:
            sorted_prices = sorted(all_prices, key=lambda x: x.price if x.price > 0 else float('inf'))
            valid_prices = [p for p in sorted_prices if p.price > 0]
            
            if valid_prices:
                cheapest = valid_prices[0]
                most_expensive = valid_prices[-1]
                savings = most_expensive.price - cheapest.price if len(valid_prices) > 1 else 0
                print(f"[PriceSearch] Cheapest: ₹{cheapest.price} at {cheapest.product_url[:30] if cheapest.product_url else 'Unknown'}")
                print(f"[PriceSearch] Potential savings: ₹{savings}")
        
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
        """Search a single pharmacy."""
        try:
            return await scraper.search_with_retry(medicine_name, dosage, max_retries=1)
        except Exception as e:
            print(f"[{scraper.pharmacy_name}] Search error: {e}")
            return []
    
    def _price_to_dict(self, price: ScrapedPrice, pharmacy_id: str = None) -> Dict[str, Any]:
        """Convert ScrapedPrice to dictionary."""
        if not price:
            return None
        
        pharmacy_name = "Unknown"
        for scraper in self.scrapers:
            if pharmacy_id and scraper.pharmacy_id == pharmacy_id:
                pharmacy_name = scraper.pharmacy_name
                break
            elif price.product_url:
                if "1mg" in price.product_url:
                    pharmacy_name = "1mg"
                elif "pharmeasy" in price.product_url:
                    pharmacy_name = "PharmEasy"
                elif "netmeds" in price.product_url:
                    pharmacy_name = "Netmeds"
                elif "apollopharmacy" in price.product_url:
                    pharmacy_name = "Apollo"
        
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
        """Search prices for multiple medicines sequentially."""
        print(f"\n[PriceSearch] Searching {len(medicines)} medicines...")
        
        results = []
        total_savings = 0.0
        
        for i, medicine in enumerate(medicines):
            name = medicine.get("name", "")
            dosage = medicine.get("dosage")
            if not name:
                continue
            
            print(f"\n[Medicine {i+1}/{len(medicines)}] {name}")
            result = await self.search_medicine(name, dosage)
            results.append(result)
            total_savings += result.get("savings", 0)
        
        print(f"\n[PriceSearch] All medicines searched. Total savings: ₹{total_savings}")
        
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


async def get_price_search_service() -> PriceSearchService:
    """Create a new price search service instance."""
    return PriceSearchService()


async def search_medicine_prices(
    medicine_name: str,
    dosage: Optional[str] = None
) -> Dict[str, Any]:
    """Convenience function to search medicine prices."""
    print(f"[API] search_medicine_prices called for: {medicine_name}")
    service = await get_price_search_service()
    return await service.search_medicine(medicine_name, dosage)


async def search_multiple_medicines(medicines: List[Dict[str, str]]) -> Dict[str, Any]:
    """Convenience function to search multiple medicines."""
    print(f"[API] search_multiple_medicines called for {len(medicines)} medicines")
    service = await get_price_search_service()
    return await service.search_multiple_medicines(medicines)
