"""
Apollo Pharmacy Scraper - HTTP Only

Apollo is client-rendered so HTTP extraction has limited success.
This scraper attempts to find data but may return empty results.
Users will still get results from PharmEasy, 1mg, and Netmeds.
"""

from typing import List, Optional
import json
import re
import httpx
from urllib.parse import quote
from .base import BaseScraper, ScrapedPrice


class ApolloScraper(BaseScraper):
    """HTTP scraper for Apollo Pharmacy (best effort - site is client-rendered)."""
    
    pharmacy_name = "Apollo"
    pharmacy_id = "apollo"
    base_url = "https://www.apollopharmacy.in"
    
    async def search(self, medicine_name: str, dosage: Optional[str] = None) -> List[ScrapedPrice]:
        """Search for a medicine on Apollo Pharmacy using HTTP."""
        try:
            query = medicine_name.strip()
            if dosage:
                query = f"{medicine_name} {dosage}"
            
            search_url = f"{self.base_url}/search-medicines/{quote(query)}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    search_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    },
                    follow_redirects=True
                )
            
            if response.status_code != 200:
                print(f"Apollo returned {response.status_code}")
                return []
            
            html = response.text
            results = []
            
            # Try to find __NEXT_DATA__ first
            next_data_match = re.search(
                r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
                html,
                re.DOTALL
            )
            
            if next_data_match:
                try:
                    data = json.loads(next_data_match.group(1))
                    page_props = data.get("props", {}).get("pageProps", {})
                    
                    # Try various possible paths for products
                    products = []
                    
                    # Common paths in Next.js apps
                    for key in ["products", "searchResults", "items", "data", "medicines"]:
                        val = page_props.get(key)
                        if isinstance(val, list) and len(val) > 0:
                            products = val
                            break
                        elif isinstance(val, dict):
                            for subkey in ["products", "items", "results"]:
                                subval = val.get(subkey)
                                if isinstance(subval, list) and len(subval) > 0:
                                    products = subval
                                    break
                    
                    if products:
                        print(f"Apollo __NEXT_DATA__ found {len(products)} products")
                        for product in products[:5]:
                            parsed = self._parse_product(product)
                            if parsed:
                                results.append(parsed)
                        return results
                except json.JSONDecodeError as e:
                    print(f"Apollo JSON error: {e}")
            
            # Try to find buildId and make _next/data request
            build_match = re.search(r'"buildId":"([^"]+)"', html)
            if build_match:
                build_id = build_match.group(1)
                data_url = f"{self.base_url}/_next/data/{build_id}/search-medicines/{quote(query)}.json"
                
                async with httpx.AsyncClient(timeout=5.0) as client:
                    try:
                        data_response = await client.get(
                            data_url,
                            headers={"User-Agent": "Mozilla/5.0"},
                            follow_redirects=True
                        )
                        if data_response.status_code == 200:
                            data = data_response.json()
                            page_props = data.get("pageProps", {})
                            products = page_props.get("products", []) or page_props.get("searchResults", [])
                            
                            if products:
                                print(f"Apollo _next/data found {len(products)} products")
                                for product in products[:5]:
                                    parsed = self._parse_product(product)
                                    if parsed:
                                        results.append(parsed)
                                return results
                    except:
                        pass
            
            # Apollo is fully client-rendered - return empty
            print("Apollo: Site is client-rendered, skipping")
            return []
            
        except httpx.TimeoutException:
            print("Apollo: HTTP timeout")
            return []
        except Exception as e:
            print(f"Apollo HTTP error: {e}")
            return []
    
    def _parse_product(self, product: dict) -> Optional[ScrapedPrice]:
        try:
            name = product.get("name", "") or product.get("productName", "") or product.get("title", "")
            if not name:
                return None
            
            # Try various price fields
            price = float(
                product.get("price", 0) or 
                product.get("salePrice", 0) or 
                product.get("sellingPrice", 0) or
                product.get("finalPrice", 0) or
                0
            )
            mrp = float(product.get("mrp", 0) or product.get("originalPrice", 0) or price)
            
            if price <= 0:
                return None
            
            discount = None
            if mrp > price and mrp > 0:
                discount = round(((mrp - price) / mrp) * 100, 1)
            
            # URL construction
            slug = product.get("slug", "") or product.get("urlKey", "") or product.get("url", "")
            url = f"{self.base_url}/otc/{slug}" if slug and not slug.startswith("http") else (slug or self.base_url)
            
            return ScrapedPrice(
                product_name=name,
                price=price,
                original_price=mrp if mrp > price else None,
                discount=discount,
                pack_size=product.get("packSize", "1 Unit") or "1 Unit",
                in_stock=product.get("inStock", True),
                delivery_days=2,
                product_url=url,
                image_url=product.get("image") or product.get("imageUrl"),
                manufacturer=product.get("manufacturer", "")
            )
        except Exception:
            return None
    
    async def get_product_details(self, product_url: str) -> Optional[ScrapedPrice]:
        return None
