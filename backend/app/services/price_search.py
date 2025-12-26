"""
Price Search Service

Aggregates medicine prices from all pharmacy scrapers.
PROGRESSIVE LOADING: Returns results as each pharmacy completes.
"""

from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
import asyncio
import json

from app.services.scrapers import PharmEasyScraper, OneMgScraper, NetmedsScraper, ApolloScraper, ScrapedPrice


class PriceSearchService:
    """Service for searching and comparing medicine prices across 4 pharmacies."""
    
    def __init__(self):
        # Only 4 pharmacies - Truemeds removed (too slow/unreliable)
        self.scrapers = [
            PharmEasyScraper(),   # HTTP - Fast
            OneMgScraper(),       # Playwright - PRELOADED_STATE
            NetmedsScraper(),     # Playwright - __INITIAL_STATE__
            ApolloScraper(),      # Playwright - DOM
        ]
    
    async def search_medicine_stream(
        self, 
        medicine_name: str, 
        dosage: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream search results as each pharmacy completes.
        Yields progress updates and results progressively.
        """
        all_prices = []
        completed_pharmacies = []
        pharmacy_results = {}
        errors = []
        total_pharmacies = len(self.scrapers)
        
        # Create a queue to collect results as they come in
        result_queue = asyncio.Queue()
        
        async def search_scraper(scraper):
            """Search a single scraper and put result in queue."""
            try:
                result = await asyncio.wait_for(
                    self._search_with_pharmacy(scraper, medicine_name, dosage),
                    timeout=90.0  # 90 seconds max per pharmacy
                )
                await result_queue.put({
                    "type": "pharmacy_complete",
                    "pharmacy": scraper.pharmacy_name,
                    "pharmacy_id": scraper.pharmacy_id,
                    "results": result,
                    "error": None
                })
            except asyncio.TimeoutError:
                await result_queue.put({
                    "type": "pharmacy_complete",
                    "pharmacy": scraper.pharmacy_name,
                    "pharmacy_id": scraper.pharmacy_id,
                    "results": [],
                    "error": f"Timeout after 90s"
                })
            except Exception as e:
                await result_queue.put({
                    "type": "pharmacy_complete",
                    "pharmacy": scraper.pharmacy_name,
                    "pharmacy_id": scraper.pharmacy_id,
                    "results": [],
                    "error": str(e)
                })
        
        # Start all scrapers as concurrent tasks
        tasks = [asyncio.create_task(search_scraper(s)) for s in self.scrapers]
        
        # Yield initial status
        yield {
            "type": "started",
            "medicine_name": medicine_name,
            "total_pharmacies": total_pharmacies,
            "pharmacies": [s.pharmacy_name for s in self.scrapers],
            "message": f"Starting search across {total_pharmacies} pharmacies..."
        }
        
        # Collect results as they complete
        completed = 0
        while completed < total_pharmacies:
            try:
                # Wait for next result with 100 second overall timeout
                result = await asyncio.wait_for(result_queue.get(), timeout=100.0)
                completed += 1
                
                pharmacy_name = result["pharmacy"]
                pharmacy_id = result["pharmacy_id"]
                prices = result["results"]
                error = result["error"]
                
                completed_pharmacies.append(pharmacy_name)
                remaining = total_pharmacies - completed
                
                if error:
                    errors.append({"pharmacy": pharmacy_name, "error": error})
                elif prices:
                    pharmacy_results[pharmacy_id] = prices
                    all_prices.extend(prices)
                
                # Yield progress update with this pharmacy's results
                yield {
                    "type": "pharmacy_result",
                    "pharmacy": pharmacy_name,
                    "pharmacy_id": pharmacy_id,
                    "results_count": len(prices) if prices else 0,
                    "prices": [self._price_to_dict(p, pharmacy_id) for p in prices] if prices else [],
                    "error": error,
                    "completed": completed,
                    "remaining": remaining,
                    "completed_pharmacies": completed_pharmacies,
                    "message": f"✅ {pharmacy_name} complete ({len(prices)} results). {remaining} pharmacies remaining..." if remaining > 0 else f"✅ All {total_pharmacies} pharmacies searched!"
                }
                
            except asyncio.TimeoutError:
                # Overall timeout - stop waiting
                break
        
        # Cancel any remaining tasks
        for task in tasks:
            if not task.done():
                task.cancel()
        
        # Calculate final results
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
        
        # Yield final complete response
        yield {
            "type": "complete",
            "success": True,
            "medicine_name": medicine_name,
            "dosage": dosage,
            "total_results": len(all_prices),
            "pharmacies_searched": [s.pharmacy_name for s in self.scrapers],
            "completed_pharmacies": completed_pharmacies,
            "prices": [self._price_to_dict(p, s) for s, prices in pharmacy_results.items() for p in prices],
            "cheapest": self._price_to_dict(cheapest) if cheapest else None,
            "savings": round(savings, 2),
            "errors": errors if errors else None,
            "message": f"Search complete! Found {len(all_prices)} results from {len(completed_pharmacies)} pharmacies."
        }
    
    async def search_medicine(
        self, 
        medicine_name: str, 
        dosage: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for a medicine across all pharmacies IN PARALLEL.
        Returns final aggregated result (non-streaming).
        """
        final_result = None
        async for result in self.search_medicine_stream(medicine_name, dosage):
            if result.get("type") == "complete":
                final_result = result
        return final_result or {"success": False, "error": "Search failed"}
    
    async def _search_with_pharmacy(
        self, 
        scraper, 
        medicine_name: str, 
        dosage: Optional[str]
    ) -> List[ScrapedPrice]:
        """Search a single pharmacy with error handling."""
        try:
            return await scraper.search_with_retry(medicine_name, dosage, max_retries=2)
        except Exception as e:
            print(f"Error searching {scraper.pharmacy_name}: {e}")
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
        """Search prices for multiple medicines."""
        async def search_one(medicine):
            name = medicine.get("name", "")
            dosage = medicine.get("dosage")
            if not name:
                return None
            return await self.search_medicine(name, dosage)
        
        tasks = [search_one(m) for m in medicines]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        total_savings = 0.0
        for result in results:
            if isinstance(result, Exception) or result is None:
                continue
            valid_results.append(result)
            total_savings += result.get("savings", 0)
        
        return {
            "success": True,
            "medicines_count": len(valid_results),
            "results": valid_results,
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
    service = await get_price_search_service()
    return await service.search_medicine(medicine_name, dosage)


async def search_medicine_prices_stream(
    medicine_name: str,
    dosage: Optional[str] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """Stream medicine price search results progressively."""
    service = await get_price_search_service()
    async for result in service.search_medicine_stream(medicine_name, dosage):
        yield result


async def search_multiple_medicines(medicines: List[Dict[str, str]]) -> Dict[str, Any]:
    """Convenience function to search multiple medicines."""
    service = await get_price_search_service()
    return await service.search_multiple_medicines(medicines)
