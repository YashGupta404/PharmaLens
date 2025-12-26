"""
Netmeds Scraper - HTTP Only (Fixed)

Uses Netmeds __INITIAL_STATE__ with improved regex.
"""

from typing import List, Optional
import json
import re
import httpx
from urllib.parse import quote
from .base import BaseScraper, ScrapedPrice


class NetmedsScraper(BaseScraper):
    """HTTP-only scraper for Netmeds."""
    
    pharmacy_name = "Netmeds"
    pharmacy_id = "netmeds"
    base_url = "https://www.netmeds.com"
    
    async def search(self, medicine_name: str, dosage: Optional[str] = None) -> List[ScrapedPrice]:
        """Search for a medicine on Netmeds using HTTP."""
        try:
            query = f"{medicine_name} {dosage}".strip() if dosage else medicine_name.strip()
            
            # Netmeds search URL
            search_url = f"{self.base_url}/catalogsearch/result/{quote(query)}/all"
            
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
                print(f"Netmeds returned {response.status_code}")
                return []
            
            html = response.text
            results = []
            
            # Find __INITIAL_STATE__ - it's a large JSON object
            # Use a more flexible regex that captures the JSON object
            state_match = re.search(
                r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});?\s*(?:</script>|window\.)',
                html,
                re.DOTALL
            )
            
            if not state_match:
                # Try alternative pattern
                state_match = re.search(
                    r'__INITIAL_STATE__\s*=\s*(\{[^<]+\})',
                    html,
                    re.DOTALL
                )
            
            if state_match:
                try:
                    state_json = state_match.group(1).strip()
                    # Clean up any trailing issues
                    if state_json.endswith(';'):
                        state_json = state_json[:-1]
                    
                    state = json.loads(state_json)
                    
                    # Navigate to products - try different paths
                    items = []
                    
                    # Path 1: productListingPage.productlists.items
                    product_page = state.get("productListingPage", {})
                    product_lists = product_page.get("productlists", {})
                    items = product_lists.get("items", [])
                    
                    # Path 2: catalogListingPage
                    if not items:
                        catalog_page = state.get("catalogListingPage", {})
                        items = catalog_page.get("productlists", {}).get("items", [])
                    
                    # Path 3: searchPage
                    if not items:
                        search_page = state.get("searchPage", {})
                        items = search_page.get("products", [])
                    
                    print(f"Netmeds found {len(items)} products")
                    
                    for item in items[:5]:
                        parsed = self._parse_product(item)
                        if parsed:
                            results.append(parsed)
                            
                except json.JSONDecodeError as e:
                    print(f"Netmeds JSON error: {e}")
                    # Save first 1000 chars for debugging
                    print(f"JSON preview: {state_match.group(1)[:500]}")
            else:
                print("Netmeds: Could not find __INITIAL_STATE__")
            
            return results
            
        except httpx.TimeoutException:
            print("Netmeds: HTTP timeout")
            return []
        except Exception as e:
            print(f"Netmeds HTTP error: {e}")
            return []
    
    def _parse_product(self, item: dict) -> Optional[ScrapedPrice]:
        try:
            name = item.get("name", "") or item.get("productName", "")
            if not name:
                return None
            
            # Price structure varies
            price_info = item.get("price", {})
            
            if isinstance(price_info, dict):
                mrp = float(price_info.get("marked", {}).get("min", 0) or 0)
                price = float(price_info.get("effective", {}).get("min", 0) or mrp)
            else:
                # Direct price
                price = float(item.get("final_price", 0) or item.get("price", 0) or 0)
                mrp = float(item.get("mrp", 0) or price)
            
            if price <= 0:
                return None
            
            discount = None
            if mrp > price and mrp > 0:
                discount = round(((mrp - price) / mrp) * 100, 1)
            
            slug = item.get("slug", "") or item.get("url_key", "")
            url = f"{self.base_url}/{slug}" if slug else self.base_url
            
            return ScrapedPrice(
                product_name=name,
                price=price,
                original_price=mrp if mrp > price else None,
                discount=discount,
                pack_size=item.get("pack_size", "1 Unit") or "1 Unit",
                in_stock=item.get("is_in_stock", True),
                delivery_days=3,
                product_url=url,
                image_url=item.get("image") or item.get("thumbnail"),
                manufacturer=item.get("manufacturer", "")
            )
        except Exception as e:
            print(f"Netmeds parse error: {e}")
            return None
    
    async def get_product_details(self, product_url: str) -> Optional[ScrapedPrice]:
        return None
