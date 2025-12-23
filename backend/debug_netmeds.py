"""
Debug Netmeds DOM structure
"""
import asyncio
from urllib.parse import quote
from playwright.async_api import async_playwright

async def debug():
    print("=== NETMEDS DOM DEBUG ===")
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    page = await context.new_page()
    
    search_url = "https://www.netmeds.com/catalogsearch/result?q=paracetamol"
    print(f"URL: {search_url}")
    
    try:
        await page.goto(search_url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        
        # Check for various selectors
        result = await page.evaluate("""
            () => {
                return {
                    inner_container1: document.querySelectorAll('.inner-container1').length,
                    product_item: document.querySelectorAll('.product-item').length,
                    cat_item: document.querySelectorAll('.cat-item').length,
                    catalogitem: document.querySelectorAll('[class*="catalog"]').length,
                    product: document.querySelectorAll('[class*="product"]').length,
                    card: document.querySelectorAll('[class*="card"]').length,
                    h3_count: document.querySelectorAll('h3').length,
                    rupee_in_body: (document.body.innerText || '').includes('₹'),
                    
                    // Get class names of first few divs that contain prices
                    priceContainers: Array.from(document.querySelectorAll('div')).filter(d => {
                        return (d.innerText || '').includes('₹') && d.innerText.length < 500;
                    }).slice(0, 3).map(d => ({class: d.className, text: d.innerText.substring(0, 100)}))
                };
            }
        """)
        print(f"Result: {result}")
        
        # Get the first h3 parent class
        h3_info = await page.evaluate("""
            () => {
                const h3s = document.querySelectorAll('h3');
                if (h3s.length > 0) {
                    const h3 = h3s[0];
                    return {
                        h3_text: h3.innerText.substring(0, 50),
                        h3_class: h3.className,
                        parent_class: h3.parentElement ? h3.parentElement.className : 'none',
                        grandparent_class: h3.parentElement?.parentElement ? h3.parentElement.parentElement.className : 'none',
                        great_grandparent_class: h3.parentElement?.parentElement?.parentElement ? h3.parentElement.parentElement.parentElement.className : 'none'
                    };
                }
                return 'no h3 found';
            }
        """)
        print(f"H3 info: {h3_info}")
        
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(debug())
