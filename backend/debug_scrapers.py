"""
Debug script - simplified version
"""
import asyncio
from urllib.parse import quote
from playwright.async_api import async_playwright

async def debug_netmeds():
    print("\n=== NETMEDS DEBUG ===")
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    page = await context.new_page()
    
    search_url = "https://www.netmeds.com/catalogsearch/result?q=paracetamol"
    print(f"URL: {search_url}")
    
    try:
        await page.goto(search_url, wait_until="networkidle", timeout=40000)
        await asyncio.sleep(2)
        
        # Check for products on page
        result = await page.evaluate("""
            () => {
                // Check if __INITIAL_STATE__ exists
                const hasState = !!window.__INITIAL_STATE__;
                let items = [];
                
                if (hasState) {
                    const plp = window.__INITIAL_STATE__.productListingPage || {};
                    items = plp.productlists?.items || [];
                }
                
                // Alternative: look for product cards in DOM
                const productCards = document.querySelectorAll('.cat-item, .product-item, [data-product]');
                
                // Look for any price mentions
                const bodyText = document.body.innerText || '';
                const hasPrices = bodyText.includes('₹') || bodyText.includes('Rs');
                
                return {
                    hasState,
                    itemsCount: items.length,
                    productCardsCount: productCards.length,
                    hasPrices,
                    pageTitle: document.title
                };
            }
        """)
        print(f"Result: {result}")
        
    finally:
        await browser.close()
        await playwright.stop()


async def debug_truemeds():
    print("\n=== TRUEMEDS DEBUG ===")
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    page = await context.new_page()
    
    search_url = "https://www.truemeds.in/search?q=paracetamol"
    print(f"URL: {search_url}")
    
    try:
        await page.goto(search_url, wait_until="networkidle", timeout=40000)
        await asyncio.sleep(3)
        
        # Check for __NEXT_DATA__
        result = await page.evaluate("""
            () => {
                const nextDataScript = document.getElementById('__NEXT_DATA__');
                let products = [];
                
                if (nextDataScript) {
                    try {
                        const data = JSON.parse(nextDataScript.textContent);
                        const pageProps = data.props?.pageProps || {};
                        // Look for products in different possible keys
                        products = pageProps.products || pageProps.searchResults || pageProps.data?.products || [];
                    } catch (e) {}
                }
                
                // Check body text for product signs
                const bodyText = document.body.innerText || '';
                
                return {
                    hasNextData: !!nextDataScript,
                    productsCount: products.length,
                    hasMRP: bodyText.includes('MRP'),
                    hasRupee: bodyText.includes('₹'),
                    pageTitle: document.title
                };
            }
        """)
        print(f"Result: {result}")
        
        # Get __NEXT_DATA__ pageProps keys
        if result['hasNextData']:
            props_keys = await page.evaluate("""
                () => {
                    try {
                        const data = JSON.parse(document.getElementById('__NEXT_DATA__').textContent);
                        return Object.keys(data.props?.pageProps || {});
                    } catch (e) { return []; }
                }
            """)
            print(f"pageProps keys: {props_keys}")
        
    finally:
        await browser.close()
        await playwright.stop()


async def main():
    await debug_netmeds()
    await debug_truemeds()

if __name__ == "__main__":
    asyncio.run(main())
