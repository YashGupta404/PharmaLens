"""
1mg Scraper - HTTP Only (No Playwright)

Extracts data from PRELOADED_STATE in HTML - no browser needed.
Memory efficient for Render's 512MB limit.
"""

from typing import List, Optional
import json
import re
import httpx
from urllib.parse import quote
from .base import BaseScraper, ScrapedPrice


class OneMgScraper(BaseScraper):
    """HTTP-only scraper for 1mg.com - extracts PRELOADED_STATE from HTML."""
    
    pharmacy_name = "1mg"
    pharmacy_id = "1mg"
    base_url = "https://www.1mg.com"
    
    async def search(self, medicine_name: str, dosage: Optional[str] = None) -> List[ScrapedPrice]:
        """Search for a medicine on 1mg using HTTP only."""
        try:
            query = medicine_name.strip()
            if dosage:
                query = f"{medicine_name} {dosage}"
            
            search_url = f"{self.base_url}/search/all?name={quote(query)}"
            
            # Use HTTP client
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    search_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                    },
                    follow_redirects=True
                )
            
            if response.status_code != 200:
                print(f"1mg returned {response.status_code}")
                return []
            
            html = response.text
            results = []
            
            # Find PRELOADED_STATE in script - it's a stringified JSON array
            # Pattern: window.PRELOADED_STATE = ["...json string..."]
            preload_match = re.search(
                r'window\.PRELOADED_STATE\s*=\s*\[(.*?)\];',
                html,
                re.DOTALL
            )
            
            if preload_match:
                try:
                    # The content is a JSON string inside the array
                    raw_content = preload_match.group(1).strip()
                    
                    # It could be a quoted JSON string
                    if raw_content.startswith('"') or raw_content.startswith("'"):
                        # Parse the outer array to get the string
                        full_array = f"[{raw_content}]"
                        arr = json.loads(full_array)
                        if arr and isinstance(arr[0], str):
                            data = json.loads(arr[0])
                        else:
                            data = arr[0] if arr else {}
                    else:
                        # Direct JSON object
                        data = json.loads(raw_content)
                    
                    # Navigate to product list
                    search_page = data.get("searchPage", {})
                    product_list = search_page.get("productList", [])
                    
                    products = []
                    if product_list and len(product_list) > 0:
                        first_list = product_list[0]
                        if isinstance(first_list, dict):
                            products = first_list.get("data", [])
                        elif isinstance(first_list, list):
                            products = first_list
                    
                    print(f"1mg HTTP found {len(products)} products")
                    
                    for product in products[:5]:
                        parsed = self._parse_product(product)
                        if parsed:
                            results.append(parsed)
                            
                except json.JSONDecodeError as e:
                    print(f"1mg JSON parse error: {e}")
            else:
                print("1mg: No PRELOADED_STATE found in HTML")
            
            return results
            
        except httpx.TimeoutException:
            print("1mg: HTTP timeout")
            return []
        except Exception as e:
            print(f"1mg HTTP error: {e}")
            return []
    
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
