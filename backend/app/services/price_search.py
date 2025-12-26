"""
Price Search Service - FAST VERSION

Searches all 4 pharmacies and returns results as fast as possible.
Shows console logs for debugging.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from app.services.scrapers import PharmEasyScraper, OneMgScraper, NetmedsScraper, ApolloScraper, ScrapedPrice


class PriceSearchService:
    """Service for searching medicine prices across 4 pharmacies."""
    
    def __init__(self):
        print("[PriceSearch] Initializing 4 scrapers...")
        self.scrapers = [
            PharmEasyScraper(),   # HTTP - FASTEST
            OneMgScraper(),       # Playwright
            NetmedsScraper(),     # Playwright
            ApolloScraper(),      # Playwright
        ]
        print(f"[PriceSearch] Ready: PharmEasy, 1mg, Netmeds, Apollo")
    
    async def search_medicine(
        self, 
        medicine_name: str, 
        dosage: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for a medicine across all 4 pharmacies.
        Runs PharmEasy first (fast), then others in parallel.
        """
        print(f"\n{'='*60}")
        print(f"[SEARCH] Starting search for: {medicine_name}")
        print(f"{'='*60}")
        
        all_prices = []
        pharmacy_results = {}
        errors = []
        
        # First: Search PharmEasy (HTTP, super fast)
        print(f"\n[1/4] PharmEasy (HTTP - fast)...")
        try:
            pharmeasy_result = await asyncio.wait_for(
                self._search_pharmacy(self.scrapers[0], medicine_name, dosage),
                timeout=30.0
            )
            if pharmeasy_result:
                print(f"[PharmEasy] ✅ Found {len(pharmeasy_result)} results")
                pharmacy_results["pharmeasy"] = pharmeasy_result
                all_prices.extend(pharmeasy_result)
            else:
                print(f"[PharmEasy] ⚠️ No results")
        except asyncio.TimeoutError:
            print(f"[PharmEasy] ⏱️ Timeout after 30s")
            errors.append({"pharmacy": "PharmEasy", "error": "Timeout"})
        except Exception as e:
            print(f"[PharmEasy] ❌ Error: {str(e)[:50]}")
            errors.append({"pharmacy": "PharmEasy", "error": str(e)})
        
        # Then: Search other 3 in parallel (Playwright-based)
        print(f"\n[2-4/4] Searching 1mg, Netmeds, Apollo in parallel...")
        
        async def search_with_timeout(scraper, timeout=45):
            name = scraper.pharmacy_name
            try:
                result = await asyncio.wait_for(
                    self._search_pharmacy(scraper, medicine_name, dosage),
                    timeout=timeout
                )
                if result:
                    print(f"[{name}] ✅ Found {len(result)} results")
                    return (scraper.pharmacy_id, result, None)
                else:
                    print(f"[{name}] ⚠️ No results")
                    return (scraper.pharmacy_id, [], None)
            except asyncio.TimeoutError:
                print(f"[{name}] ⏱️ Timeout after {timeout}s")
                return (scraper.pharmacy_id, [], "Timeout")
            except Exception as e:
                print(f"[{name}] ❌ Error: {str(e)[:50]}")
                return (scraper.pharmacy_id, [], str(e))
        
        # Run 1mg, Netmeds, Apollo in parallel
        tasks = [search_with_timeout(s) for s in self.scrapers[1:]]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, tuple):
                pharmacy_id, prices, error = result
                if prices:
                    pharmacy_results[pharmacy_id] = prices
                    all_prices.extend(prices)
                if error:
                    errors.append({"pharmacy": pharmacy_id, "error": error})
        
        # Calculate best price
        print(f"\n[SEARCH] Complete. Total results: {len(all_prices)}")
        
        cheapest = None
        savings = 0.0
        
        if all_prices:
            valid_prices = [p for p in all_prices if p.price > 0]
            if valid_prices:
                sorted_prices = sorted(valid_prices, key=lambda x: x.price)
                cheapest = sorted_prices[0]
                most_expensive = sorted_prices[-1]
                savings = most_expensive.price - cheapest.price
                print(f"[SEARCH] Cheapest: ₹{cheapest.price} | Savings: ₹{savings}")
        
        return {
            "success": True,
            "medicine_name": medicine_name,
            "dosage": dosage,
            "total_results": len(all_prices),
            "pharmacies_searched": ["PharmEasy", "1mg", "Netmeds", "Apollo"],
            "prices": [self._price_to_dict(p, pid) for pid, prices in pharmacy_results.items() for p in prices],
            "cheapest": self._price_to_dict(cheapest) if cheapest else None,
            "savings": round(savings, 2),
            "errors": errors if errors else None
        }
    
    async def _search_pharmacy(self, scraper, medicine_name: str, dosage: Optional[str]) -> List[ScrapedPrice]:
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
        if price.product_url:
            if "1mg" in price.product_url:
                pharmacy_name = "1mg"
                pharmacy_id = pharmacy_id or "1mg"
            elif "pharmeasy" in price.product_url:
                pharmacy_name = "PharmEasy"
                pharmacy_id = pharmacy_id or "pharmeasy"
            elif "netmeds" in price.product_url:
                pharmacy_name = "Netmeds"
                pharmacy_id = pharmacy_id or "netmeds"
            elif "apollopharmacy" in price.product_url:
                pharmacy_name = "Apollo"
                pharmacy_id = pharmacy_id or "apollo"
        
        return {
            "pharmacy_id": pharmacy_id or "unknown",
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
    
    async def search_multiple_medicines(self, medicines: List[Dict[str, str]]) -> Dict[str, Any]:
        """Search prices for multiple medicines."""
        print(f"\n[MULTI] Searching {len(medicines)} medicines...")
        
        results = []
        total_savings = 0.0
        
        for i, medicine in enumerate(medicines):
            name = medicine.get("name", "")
            dosage = medicine.get("dosage")
            if not name:
                continue
            
            print(f"\n[MULTI] Medicine {i+1}/{len(medicines)}: {name}")
            result = await self.search_medicine(name, dosage)
            results.append(result)
            total_savings += result.get("savings", 0)
        
        print(f"\n[MULTI] All done. Total savings: ₹{total_savings}")
        
        return {
            "success": True,
            "medicines_count": len(results),
            "results": results,
            "total_savings": round(total_savings, 2)
        }


# Convenience functions
async def search_medicine_prices(medicine_name: str, dosage: Optional[str] = None) -> Dict[str, Any]:
    print(f"[API] search_medicine_prices called: {medicine_name}")
    service = PriceSearchService()
    return await service.search_medicine(medicine_name, dosage)


async def search_multiple_medicines(medicines: List[Dict[str, str]]) -> Dict[str, Any]:
    print(f"[API] search_multiple_medicines called: {len(medicines)} medicines")
    service = PriceSearchService()
    return await service.search_multiple_medicines(medicines)
