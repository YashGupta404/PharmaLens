"""
Truemeds Scraper - Stealth Mode (Playwright)

Uses stealth browser techniques to bypass bot detection:
- Realistic browser fingerprinting
- Anti-webdriver detection
- Home page visit for cookies
"""

from typing import List, Optional
import random
import asyncio
from urllib.parse import quote
from .base import BaseScraper, ScrapedPrice
from playwright.async_api import async_playwright


class TruemedsScraper(BaseScraper):
    """Scraper for Truemeds using Playwright with stealth mode."""
    
    pharmacy_name = "Truemeds"
    pharmacy_id = "truemeds"
    base_url = "https://www.truemeds.in"
    
    async def search(self, medicine_name: str, dosage: Optional[str] = None) -> List[ScrapedPrice]:
        """Search for a medicine on Truemeds using stealth browser."""
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
            
            # Navigate to search page - use the search URL path format
            search_url = f"{self.base_url}/search/{quote(query)}"
            await page.goto(search_url, wait_until="networkidle", timeout=30000)
            
            # Wait for content with random delay
            await asyncio.sleep(random.uniform(2, 4))
            
            # Extract products from DOM
            products = await page.evaluate("""
                () => {
                    const products = [];
                    const seen = new Set();
                    
                    // Truemeds renders products as divs - look for price indicators
                    const allDivs = Array.from(document.querySelectorAll('div'));
                    
                    for (const div of allDivs) {
                        const text = div.innerText || '';
                        
                        // Product cards contain ₹, MRP text, and are reasonably sized
                        if (text.includes('₹') && text.length > 20 && text.length < 500) {
                            // Check for Add to Cart or similar to confirm it's a product card
                            if (text.includes('Add') || text.includes('MRP')) {
                                const lines = text.split('\\n').filter(l => l.trim());
                                
                                // Find product name
                                let name = '';
                                for (const line of lines) {
                                    const trimmed = line.trim();
                                    if (trimmed.length > 5 && 
                                        !trimmed.includes('₹') && 
                                        !trimmed.includes('MRP') &&
                                        !trimmed.includes('Add') &&
                                        !trimmed.includes('OFF') &&
                                        !trimmed.includes('%') &&
                                        !trimmed.toLowerCase().includes('substitute')) {
                                        name = trimmed;
                                        break;
                                    }
                                }
                                
                                if (!name || seen.has(name)) continue;
                                
                                // Extract selling price (first ₹ amount)
                                let price = 0;
                                const priceMatch = text.match(/₹\\s*([\\d,.]+)/);
                                if (priceMatch) {
                                    price = parseFloat(priceMatch[1].replace(/,/g, ''));
                                }
                                
                                // Extract MRP from del tag or MRP text
                                let mrp = 0;
                                const del = div.querySelector('del');
                                if (del) {
                                    const m = del.textContent.match(/([\\d,.]+)/);
                                    if (m) mrp = parseFloat(m[1].replace(/,/g, ''));
                                }
                                if (!mrp) {
                                    const mrpMatch = text.match(/MRP[:\\s]*₹?\\s*([\\d,.]+)/);
                                    if (mrpMatch) mrp = parseFloat(mrpMatch[1].replace(/,/g, ''));
                                }
                                
                                // Extract discount
                                let discount = null;
                                const discMatch = text.match(/(\\d+)%\\s*OFF/i);
                                if (discMatch) discount = parseFloat(discMatch[1]);
                                
                                if (name && price > 0) {
                                    seen.add(name);
                                    products.push({
                                        name: name,
                                        price: price,
                                        mrp: mrp || price,
                                        discount: discount
                                    });
                                }
                                
                                if (products.length >= 5) break;
                            }
                        }
                    }
                    
                    return products;
                }
            """)
            
            await context.close()
            
            results = []
            for product in products:
                name = product.get("name", "")
                price = float(product.get("price", 0))
                mrp = float(product.get("mrp", price))
                
                if not name or price <= 0:
                    continue
                
                discount = product.get("discount")
                if discount is None and mrp > price:
                    discount = round(((mrp - price) / mrp) * 100, 1)
                
                results.append(ScrapedPrice(
                    product_name=name,
                    price=price,
                    original_price=mrp if mrp > price else None,
                    discount=discount,
                    pack_size="1 Unit",
                    in_stock=True,
                    delivery_days=2,
                    product_url=search_url,
                    image_url=None,
                    manufacturer=""
                ))
            
            print(f"Truemeds stealth found {len(results)} products")
            return results
            
        except Exception as e:
            print(f"Truemeds error: {e}")
            return []
        finally:
            if browser:
                try: await browser.close()
                except: pass
            if playwright:
                try: await playwright.stop()
                except: pass
    
    async def get_product_details(self, product_url: str) -> Optional[ScrapedPrice]:
        return None
