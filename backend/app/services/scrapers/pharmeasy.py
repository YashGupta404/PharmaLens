"""
PharmEasy Scraper - Verified with Browser Research

Correct path: window.__NEXT_DATA__ → props.pageProps.searchResults
Price fields: salePriceDecimal, mrpDecimal, discountPercent
"""

from typing import List, Optional
import json
import re
from urllib.parse import quote
from .base import BaseScraper, ScrapedPrice


class PharmEasyScraper(BaseScraper):
    """Scraper for PharmEasy pharmacy."""
    
    pharmacy_name = "PharmEasy"
    pharmacy_id = "pharmeasy"
    base_url = "https://pharmeasy.in"
    
    async def search(self, medicine_name: str, dosage: Optional[str] = None) -> List[ScrapedPrice]:
        """Search for a medicine on PharmEasy."""
        try:
            client = await self._get_client()
            
            query = medicine_name.strip()
            if dosage:
                query = f"{medicine_name} {dosage}"
            
            search_url = f"{self.base_url}/search/all?name={quote(query)}"
            
            response = await client.get(search_url)
            
            if response.status_code != 200:
                print(f"PharmEasy returned {response.status_code}")
                return []
            
            html = response.text
            results = []
            
            # Find __NEXT_DATA__
            next_data_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
            
            if next_data_match:
                try:
                    data = json.loads(next_data_match.group(1))
                    page_props = data.get("props", {}).get("pageProps", {})
                    
                    # CORRECT PATH: searchResults (not productListing)
                    products = (
                        page_props.get("searchResults", []) or
                        page_props.get("productListing", {}).get("products", []) or
                        page_props.get("products", []) or
                        []
                    )
                    
                    print(f"PharmEasy found {len(products)} products")
                    
                    for product in products[:5]:
                        parsed = self._parse_product(product, search_url)
                        if parsed:
                            results.append(parsed)
                            
                except json.JSONDecodeError as e:
                    print(f"PharmEasy JSON error: {e}")
            else:
                print("PharmEasy: No __NEXT_DATA__ found")
            
            return results
            
        except Exception as e:
            print(f"PharmEasy error: {e}")
            return []
    
    def _parse_product(self, product: dict, fallback_url: str) -> Optional[ScrapedPrice]:
        """Parse product data."""
        try:
            name = product.get("name", "") or product.get("productName", "")
            if not name:
                return None
            
            # Use decimal prices (more accurate)
            mrp = float(product.get("mrpDecimal", 0) or product.get("mrp", 0) or 0)
            sale_price = float(
                product.get("salePriceDecimal", 0) or 
                product.get("salePrice", 0) or 
                product.get("price", 0) or 
                0
            )
            
            price = sale_price if sale_price > 0 else mrp
            if price <= 0:
                return None
            
            # Discount
            discount = None
            if product.get("discountPercent"):
                discount = float(str(product.get("discountPercent")).replace("%", ""))
            elif mrp > 0 and sale_price > 0 and mrp > sale_price:
                discount = round(((mrp - sale_price) / mrp) * 100, 1)
            
            # URL
            slug = product.get("slug", "") or product.get("productSlug", "")
            product_url = f"{self.base_url}/online-medicine-order/{slug}" if slug else fallback_url
            
            # Pack size
            pack_size = product.get("packDesc", "") or product.get("packSize", "") or "1 Unit"
            
            # Image
            image = product.get("image", {})
            image_url = image.get("url") if isinstance(image, dict) else image
            
            return ScrapedPrice(
                product_name=name,
                price=price,
                original_price=mrp if mrp > sale_price else None,
                discount=discount,
                pack_size=str(pack_size),
                in_stock=product.get("isInStock", True),
                delivery_days=1,
                product_url=product_url,
                image_url=image_url,
                manufacturer=product.get("manufacturer", "")
            )
        except Exception as e:
            print(f"PharmEasy product parse error: {e}")
            return None
    
    async def get_product_details(self, product_url: str) -> Optional[ScrapedPrice]:
        return None
