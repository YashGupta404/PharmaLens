"""
Test with anti-bot bypass techniques
"""
import asyncio
from urllib.parse import quote
from playwright.async_api import async_playwright

async def test_netmeds():
    print("=== NETMEDS ANTI-BOT TEST ===")
    
    playwright = await async_playwright().start()
    # Try with more realistic settings
    browser = await playwright.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process"
        ]
    )
    
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        java_script_enabled=True,
        locale="en-IN"
    )
    
    page = await context.new_page()
    
    # Anti-bot: modify navigator.webdriver
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        window.chrome = { runtime: {} };
    """)
    
    search_url = "https://www.netmeds.com/catalogsearch/result?q=paracetamol"
    print(f"URL: {search_url}")
    
    try:
        response = await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
        print(f"Status: {response.status}")
        await asyncio.sleep(3)
        
        # Check current URL (may have redirected)
        print(f"Current URL: {page.url}")
        
        # Check for CAPTCHA or blocking
        body_text = await page.evaluate("() => document.body.innerText.substring(0, 500)")
        print(f"Body sample: {body_text[:200]}")
        
        # Check title
        title = await page.title()
        print(f"Title: {title}")
        
        # Take screenshot for debugging
        await page.screenshot(path="netmeds_test.png")
        print("Screenshot saved to netmeds_test.png")
        
    finally:
        await browser.close()
        await playwright.stop()


async def test_truemeds():
    print("\n=== TRUEMEDS ANTI-BOT TEST ===")
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled"
        ]
    )
    
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080}
    )
    
    page = await context.new_page()
    
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    
    search_url = "https://www.truemeds.in/search/paracetamol"
    print(f"URL: {search_url}")
    
    try:
        response = await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
        print(f"Status: {response.status}")
        await asyncio.sleep(3)
        
        print(f"Current URL: {page.url}")
        
        body_text = await page.evaluate("() => document.body.innerText.substring(0, 500)")
        print(f"Body sample: {body_text[:200]}")
        
        title = await page.title()
        print(f"Title: {title}")
        
        await page.screenshot(path="truemeds_test.png")
        print("Screenshot saved to truemeds_test.png")
        
    finally:
        await browser.close()
        await playwright.stop()


async def main():
    await test_netmeds()
    await test_truemeds()

if __name__ == "__main__":
    asyncio.run(main())
