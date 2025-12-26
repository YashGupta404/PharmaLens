"""
Price Search Service - OPTIMIZED VERSION

Strategy:
- PharmEasy + 1mg: HTTP (fast, instant results)
- Netmeds + Apollo: Playwright (one at a time to save RAM)
- All run in parallel, results shown as they arrive
- Semaphore limits Playwright to 1 concurrent browser (saves RAM)
- Medicine names are cleaned and normalized for better matches
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from app.services.scrapers import PharmEasyScraper, OneMgScraper, NetmedsScraper, ApolloScraper, ScrapedPrice
from app.services.medicine_utils import clean_medicine_name, get_search_query, get_alternative_names

# Semaphore to limit Playwright browsers to 1 at a time (saves ~200MB RAM)
PLAYWRIGHT_SEMAPHORE = asyncio.Semaphore(1)


class PriceSearchService:
    """Service for searching medicine prices across 4 pharmacies."""
    
    def __init__(self):
        print("[PriceSearch] Initializing scrapers...")
        # HTTP scrapers (fast, no browser)
        self.http_scrapers = [
            PharmEasyScraper(),   # HTTP
            OneMgScraper(),       # HTTP
        ]
        # Playwright scrapers (need browser, run one at a time)
        self.playwright_scrapers = [
            NetmedsScraper(),     # Playwright
            ApolloScraper(),      # Playwright
        ]
        print(f"[PriceSearch] Ready: PharmEasy, 1mg (HTTP) | Netmeds, Apollo (Playwright)")
    
    async def search_medicine(
        self, 
        medicine_name: str, 
        dosage: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for a medicine across all 4 pharmacies.
        HTTP scrapers run freely, Playwright scrapers limited to 1 at a time.
        """
        # Clean and optimize the search query
        original_name = medicine_name
        search_query = get_search_query(medicine_name, dosage)
        alternatives = get_alternative_names(medicine_name)
        
        print(f"\n{'='*60}")
        print(f"[SEARCH] Original: {original_name}")
        print(f"[SEARCH] Optimized query: {search_query}")
        if alternatives:
            print(f"[SEARCH] Known alternatives: {', '.join(alternatives[:3])}")
        print(f"{'='*60}")
        
        all_prices = []
        pharmacy_results = {}
        errors = []
        
        start_time = datetime.now()
        
        async def search_http(scraper, query, timeout=15):
            """Search using HTTP scraper (no semaphore needed)."""
            name = scraper.pharmacy_name
            try:
                print(f"[{name}] Starting HTTP search...")
                result = await asyncio.wait_for(
                    scraper.search(query, None),  # Query already includes dosage
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
        
        async def search_playwright(scraper, query, timeout=30):
            """Search using Playwright scraper (limited by semaphore)."""
            name = scraper.pharmacy_name
            try:
                # Wait for semaphore - only 1 Playwright browser at a time
                async with PLAYWRIGHT_SEMAPHORE:
                    print(f"[{name}] Starting Playwright search...")
                    result = await asyncio.wait_for(
                        scraper.search(query, None),  # Query already includes dosage
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
        
        # Create all tasks
        print(f"\n[SEARCH] Launching all 4 pharmacy searches...")
        
        tasks = []
        # HTTP scrapers - no limit
        for scraper in self.http_scrapers:
            tasks.append(search_http(scraper, search_query, timeout=15))
        # Playwright scrapers - limited by semaphore
        for scraper in self.playwright_scrapers:
            tasks.append(search_playwright(scraper, search_query, timeout=30))
        
        # Run all in parallel (semaphore handles Playwright limiting)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n[SEARCH] All searches completed in {elapsed:.1f}s")
        
        # Process results
        for result in results:
            if isinstance(result, tuple):
                pharmacy_id, prices, error = result
                if prices:
                    pharmacy_results[pharmacy_id] = prices
                    all_prices.extend(prices)
                if error:
                    errors.append({"pharmacy": pharmacy_id, "error": error})
            elif isinstance(result, Exception):
                print(f"[SEARCH] Task exception: {result}")
        
        # Calculate best price
        print(f"[SEARCH] Total results: {len(all_prices)}")
        
        cheapest = None
        savings = 0.0
        
        if all_prices:
            valid_prices = [p for p in all_prices if p.price > 0]
            if valid_prices:
                sorted_prices = sorted(valid_prices, key=lambda x: x.price)
                cheapest = sorted_prices[0]
                most_expensive = sorted_prices[-1]
                savings = most_expensive.price - cheapest.price
                print(f"[SEARCH] Cheapest: ₹{cheapest.price} | Savings: ₹{savings:.2f}")
        
        return {
            "success": True,
            "medicine_name": original_name,
            "search_query": search_query,
            "alternatives": alternatives[:3] if alternatives else None,
            "dosage": dosage,
            "total_results": len(all_prices),
            "pharmacies_searched": ["PharmEasy", "1mg", "Netmeds", "Apollo"],
            "prices": [self._price_to_dict(p, pid) for pid, prices in pharmacy_results.items() for p in prices],
            "cheapest": self._price_to_dict(cheapest) if cheapest else None,
            "savings": round(savings, 2),
            "search_time_seconds": round(elapsed, 1),
            "errors": errors if errors else None
        }
    
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
