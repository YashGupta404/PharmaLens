"""
Apollo Pharmacy Scraper - DOM Extraction

Uses sync_playwright with asyncio.to_thread for uvicorn compatibility.
"""

from typing import List, Optional
import asyncio
from urllib.parse import quote
from .base import BaseScraper, ScrapedPrice
from playwright.sync_api import sync_playwright


class ApolloScraper(BaseScraper):
    """Scraper for Apollo Pharmacy using DOM extraction."""
    
    pharmacy_name = "Apollo"
    pharmacy_id = "apollo"
    base_url = "https://www.apollopharmacy.in"
    
    def _sync_search(self, medicine_name: str, dosage: Optional[str] = None) -> List[ScrapedPrice]:
        """Sync version of search to run in thread pool."""
        try:
            query = medicine_name.strip()
            if dosage:
                query = f"{medicine_name} {dosage}"
            
            search_url = f"{self.base_url}/search-medicines/{quote(query)}"
            
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"]
                )
                
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                # Navigate and wait for products to load
                page.goto(search_url, wait_until="networkidle", timeout=30000)
                
                # Wait for product cards to appear
                try:
                    page.wait_for_selector("a.cardAnchorStyle", timeout=8000)
                except Exception:
                    print("Apollo: No product cards found")
                    context.close()
                    browser.close()
                    return []
                
                # Extract products using verified DOM selectors
                products = page.evaluate("""
                    () => {
                        const cards = Array.from(document.querySelectorAll('a.cardAnchorStyle'));
                        return cards.slice(0, 5).map(card => {
                            // Get product name from first h2
                            const h2Elements = card.querySelectorAll('h2');
                            const name = h2Elements[0]?.textContent?.trim() || '';
                            const packing = h2Elements[1]?.textContent?.trim() || '';
                            
                            // Find price in p elements containing ₹
                            const pElements = Array.from(card.querySelectorAll('p'));
                            let price = 0;
                            let priceText = '';
                            
                            for (const p of pElements) {
                                const text = p.textContent || '';
                                if (text.includes('₹')) {
                                    priceText = text;
                                    const match = text.match(/₹\\s*([\\d,.]+)/);
                                    if (match) {
                                        price = parseFloat(match[1].replace(',', ''));
                                        break;
                                    }
                                }
                            }
                            
                            // Get URL
                            const url = card.href || '';
                            
                            return {
                                name: name,
                                packing: packing,
                                price: price,
                                priceText: priceText,
                                url: url
                            };
                        }).filter(p => p.name && p.price > 0);
                    }
                """)
                
                context.close()
                browser.close()
            
            # Convert to ScrapedPrice objects
            results = []
            for product in products:
                try:
                    full_name = product.get("name", "")
                    packing = product.get("packing", "")
                    if packing:
                        full_name = f"{full_name} {packing}"
                    
                    price = float(product.get("price", 0))
                    if price <= 0:
                        continue
                    
                    results.append(ScrapedPrice(
                        product_name=full_name,
                        price=price,
                        original_price=None,  # Apollo shows final price
                        discount=None,
                        pack_size=packing or "1 Unit",
                        in_stock=True,
                        delivery_days=2,
                        product_url=product.get("url", search_url),
                        image_url=None,
                        manufacturer=""
                    ))
                except Exception as e:
                    print(f"Apollo product parse error: {e}")
                    continue
            
            print(f"Apollo DOM found {len(results)} products")
            return results
            
        except Exception as e:
            print(f"Apollo error: {e}")
            return []
    
    async def search(self, medicine_name: str, dosage: Optional[str] = None) -> List[ScrapedPrice]:
        """Search for a medicine on Apollo Pharmacy (runs in thread pool)."""
        return await asyncio.to_thread(self._sync_search, medicine_name, dosage)
    
    async def get_product_details(self, product_url: str) -> Optional[ScrapedPrice]:
        return None
