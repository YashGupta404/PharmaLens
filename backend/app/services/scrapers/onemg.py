from typing import List, Optional
import json
import asyncio
from urllib.parse import quote
from .base import BaseScraper, ScrapedPrice
from playwright.sync_api import sync_playwright


class OneMgScraper(BaseScraper):
    """Scraper for 1mg.com using Playwright headless browser."""
    
    pharmacy_name = "1mg"
    pharmacy_id = "1mg"
    base_url = "https://www.1mg.com"
    
    def _sync_search(self, medicine_name: str, dosage: Optional[str] = None) -> List[ScrapedPrice]:
        """Sync version of search to run in thread pool."""
        try:
            query = medicine_name.strip()
            if dosage:
                query = f"{medicine_name} {dosage}"
            
            search_url = f"{self.base_url}/search/all?name={quote(query)}"
            
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1000)
                
                # Extract PRELOADED_STATE - it's JSON string in array
                products = page.evaluate("""
                    () => {
                        try {
                            const state = window.PRELOADED_STATE;
                            if (!state) return [];
                            
                            let data = state;
                            if (Array.isArray(state) && state.length > 0) {
                                data = typeof state[0] === 'string' ? JSON.parse(state[0]) : state[0];
                            }
                            
                            const searchPage = data.searchPage || {};
                            const productList = searchPage.productList || [];
                            if (productList.length > 0 && productList[0].data) {
                                return productList[0].data.slice(0, 5);
                            }
                            return [];
                        } catch (e) {
                            console.error(e);
                            return [];
                        }
                    }
                """)
                
                context.close()
                browser.close()
            
            results = []
            for product in products:
                parsed = self._parse_product(product)
                if parsed:
                    results.append(parsed)
            
            print(f"1mg Playwright found {len(results)} products")
            return results
            
        except Exception as e:
            print(f"1mg error: {e}")
            return []
    
    async def search(self, medicine_name: str, dosage: Optional[str] = None) -> List[ScrapedPrice]:
        """Search for a medicine on 1mg using headless browser (runs in thread pool)."""
        return await asyncio.to_thread(self._sync_search, medicine_name, dosage)
    
    def _parse_product(self, product: dict) -> Optional[ScrapedPrice]:
        try:
            name = product.get("name", "")
            if not name:
                return None
            
            mrp = float(product.get("price", 0) or 0)
            selling = float(product.get("discountedPrice", 0) or mrp)
            price = selling if selling > 0 else mrp
            
            if price <= 0:
                return None
            
            discount = None
            if mrp > 0 and selling > 0 and mrp > selling:
                discount = round(((mrp - selling) / mrp) * 100, 1)
            
            url = product.get("url", "")
            if url and not url.startswith("http"):
                url = f"{self.base_url}{url}"
            
            return ScrapedPrice(
                product_name=name,
                price=price,
                original_price=mrp if mrp > selling else None,
                discount=discount,
                pack_size=product.get("packSizeLabel", "1 Unit"),
                in_stock=product.get("available", True),
                delivery_days=2,
                product_url=url or self.base_url,
                image_url=product.get("image"),
                manufacturer=product.get("manufacturer", "")
            )
        except Exception:
            return None
    
    async def get_product_details(self, product_url: str) -> Optional[ScrapedPrice]:
        return None
