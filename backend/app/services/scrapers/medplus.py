"""
MedPlus Pharmacy Scraper - Stealth Mode

MedPlus uses bot detection. This version uses:
- Realistic browser fingerprinting
- Randomized delays
- Full browser context (cookies, storage)
- Stealth evasion techniques
"""

from typing import List, Optional
import random
import asyncio
from urllib.parse import quote
from .base import BaseScraper, ScrapedPrice
from playwright.async_api import async_playwright


class MedPlusScraper(BaseScraper):
    """Scraper for MedPlus pharmacy with stealth mode."""
    
    pharmacy_name = "MedPlus"
    pharmacy_id = "medplus"
    base_url = "https://www.medplusmart.com"
    
    async def search(self, medicine_name: str, dosage: Optional[str] = None) -> List[ScrapedPrice]:
        """Search for a medicine on MedPlus using stealth browser."""
        playwright = None
        browser = None
        
        try:
            query = medicine_name.strip()
            if dosage:
                query = f"{medicine_name} {dosage}"
            
            playwright = await async_playwright().start()
            
            # Launch with stealth settings
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--disable-infobars",
                    "--window-size=1920,1080",
                ]
            )
            
            # Create context with realistic fingerprint
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="en-IN",
                timezone_id="Asia/Kolkata",
                geolocation={"longitude": 77.5946, "latitude": 12.9716},
                permissions=["geolocation"],
                java_script_enabled=True,
            )
            
            # Add stealth scripts
            await context.add_init_script("""
                // Override navigator properties to appear as real browser
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-IN', 'en-US', 'en']});
                
                // Override Chrome detection
                window.chrome = {runtime: {}};
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({state: Notification.permission}) :
                        originalQuery(parameters)
                );
            """)
            
            page = await context.new_page()
            
            # First visit home page to get cookies
            try:
                await page.goto(self.base_url, wait_until="domcontentloaded", timeout=10000)
                await asyncio.sleep(random.uniform(1, 2))
            except Exception:
                pass
            
            # Now navigate to search
            search_url = f"{self.base_url}/searchProduct.mart?searchKey={quote(query)}"
            await page.goto(search_url, wait_until="networkidle", timeout=15000)
            
            # Wait for products with random delay
            await asyncio.sleep(random.uniform(1.5, 3))
            
            try:
                await page.wait_for_selector(".product-card, a[href*='/product/'], [class*='product']", timeout=8000)
            except Exception:
                print("MedPlus: No products found after wait")
                await context.close()
                return []
            
            # Extract products
            products = await page.evaluate("""
                () => {
                    const products = [];
                    
                    // Try multiple selectors
                    const selectors = [
                        '.product-card',
                        'a[href*="/product/"]',
                        '[class*="product-item"]',
                        '[class*="productCard"]'
                    ];
                    
                    let cards = [];
                    for (const sel of selectors) {
                        const found = document.querySelectorAll(sel);
                        if (found.length > 0) {
                            cards = found;
                            break;
                        }
                    }
                    
                    cards.forEach((card, i) => {
                        if (i >= 5) return;
                        
                        try {
                            // Get name
                            let name = '';
                            const h6 = card.querySelector('h6');
                            const spanTitle = card.querySelector('[title]');
                            const h5 = card.querySelector('h5');
                            
                            if (spanTitle) {
                                name = spanTitle.getAttribute('title') || spanTitle.textContent;
                            } else if (h6) {
                                name = h6.textContent;
                            } else if (h5) {
                                name = h5.textContent;
                            }
                            name = (name || '').trim();
                            
                            // Get price
                            let price = 0;
                            const allText = card.innerText || '';
                            const priceMatch = allText.match(/₹\\s*([\\d,.]+)/);
                            if (priceMatch) {
                                price = parseFloat(priceMatch[1].replace(',', ''));
                            }
                            
                            // Get URL
                            let url = '';
                            if (card.tagName === 'A') {
                                url = card.href;
                            } else {
                                const link = card.querySelector('a[href*="/product/"]');
                                if (link) url = link.href;
                            }
                            
                            if (name && price > 0) {
                                products.push({name, price, url});
                            }
                        } catch (e) {}
                    });
                    
                    return products;
                }
            """)
            
            await context.close()
            
            # Convert to ScrapedPrice
            results = []
            for product in products:
                try:
                    results.append(ScrapedPrice(
                        product_name=product.get("name", ""),
                        price=float(product.get("price", 0)),
                        original_price=None,
                        discount=None,
                        pack_size="1 Unit",
                        in_stock=True,
                        delivery_days=2,
                        product_url=product.get("url", self.base_url),
                        image_url=None,
                        manufacturer=""
                    ))
                except Exception:
                    continue
            
            print(f"MedPlus stealth found {len(results)} products")
            return results
            
        except Exception as e:
            print(f"MedPlus error: {e}")
            return []
        finally:
            if browser:
                try:
                    await browser.close()
                except Exception:
                    pass
            if playwright:
                try:
                    await playwright.stop()
                except Exception:
                    pass
    
    async def get_product_details(self, product_url: str) -> Optional[ScrapedPrice]:
        return None
