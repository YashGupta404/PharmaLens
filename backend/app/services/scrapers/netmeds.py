"""
Netmeds Scraper - Using /products?q= URL format

Uses sync_playwright with asyncio.to_thread for uvicorn compatibility.
"""

from typing import List, Optional
import asyncio
from urllib.parse import quote
from .base import BaseScraper, ScrapedPrice
from playwright.sync_api import sync_playwright


class NetmedsScraper(BaseScraper):
    pharmacy_name = "Netmeds"
    pharmacy_id = "netmeds"
    base_url = "https://www.netmeds.com"
    
    def _sync_search(self, medicine_name: str, dosage: Optional[str] = None) -> List[ScrapedPrice]:
        """Sync version of search to run in thread pool."""
        try:
            query = f"{medicine_name} {dosage}".strip() if dosage else medicine_name.strip()
            
            # Use /products?q= format (this is what works in browser)
            search_url = f"{self.base_url}/products?q={quote(query)}"
            
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
                page = browser.new_page()
                
                page.goto(search_url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(3000)
                
                # Extract from __INITIAL_STATE__
                products = page.evaluate("""
                    () => {
                        try {
                            const items = window.__INITIAL_STATE__?.productListingPage?.productlists?.items || [];
                            return items.slice(0, 5).map(item => ({
                                name: item.name,
                                mrp: item.price?.marked?.min || 0,
                                price: item.price?.effective?.min || 0,
                                slug: item.slug
                            }));
                        } catch (e) { return []; }
                    }
                """)
                
                browser.close()
            
            results = []
            for p in products:
                if not p.get("name") or not p.get("price"):
                    continue
                    
                price = float(p["price"])
                mrp = float(p.get("mrp", price))
                discount = round(((mrp - price) / mrp) * 100, 1) if mrp > price else None
                
                results.append(ScrapedPrice(
                    product_name=p["name"],
                    price=price,
                    original_price=mrp if mrp > price else None,
                    discount=discount,
                    pack_size="1 Unit",
                    in_stock=True,
                    delivery_days=3,
                    product_url=f"{self.base_url}/{p.get('slug', '')}" if p.get('slug') else search_url
                ))
            
            print(f"Netmeds found {len(results)} products")
            return results
            
        except Exception as e:
            print(f"Netmeds error: {e}")
            return []
    
    async def search(self, medicine_name: str, dosage: Optional[str] = None) -> List[ScrapedPrice]:
        """Search for a medicine on Netmeds (runs in thread pool)."""
        return await asyncio.to_thread(self._sync_search, medicine_name, dosage)
    
    async def get_product_details(self, product_url: str) -> Optional[ScrapedPrice]:
        return None
