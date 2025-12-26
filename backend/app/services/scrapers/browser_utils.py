"""
Browser Utility for Headless Scraping

Provides Playwright browser functionality for scraping JavaScript-rendered pharmacy websites.
Handles stringified JSON state (like 1mg's PRELOADED_STATE[0]).
"""

from playwright.async_api import async_playwright, Browser, BrowserContext
from typing import Optional, Dict, Any, List
import asyncio
import json


async def get_page_with_js(url: str, wait_selector: str = None, timeout: int = 10000) -> Dict[str, Any]:
    """
    Fetch a page with JavaScript rendering using Playwright.
    
    Args:
        url: URL to fetch
        wait_selector: CSS selector to wait for (optional)
        timeout: Maximum time to wait in ms
    
    Returns:
        Dict with 'html', 'state' (JS state objects), and 'success'
    """
    playwright = None
    browser = None
    
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox"
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Navigate to page
        await page.goto(url, wait_until="networkidle", timeout=timeout)
        
        # Wait for content if selector provided
        if wait_selector:
            try:
                await page.wait_for_selector(wait_selector, timeout=3000)
            except Exception:
                pass
        
        # Get HTML content
        html = await page.content()
        
        # Extract JavaScript state objects with proper parsing
        state_data = await page.evaluate("""
            () => {
                const result = {};
                
                // Try PRELOADED_STATE - handle both object and stringified array
                if (window.PRELOADED_STATE) {
                    let ps = window.PRELOADED_STATE;
                    
                    // If it's an array with string elements (like 1mg), parse them
                    if (Array.isArray(ps) && ps.length > 0) {
                        result.PRELOADED_STATE = ps.map(item => {
                            if (typeof item === 'string') {
                                try {
                                    return JSON.parse(item);
                                } catch (e) {
                                    return item;
                                }
                            }
                            return item;
                        });
                    } else {
                        result.PRELOADED_STATE = ps;
                    }
                }
                
                // Try __NEXT_DATA__
                const nextData = document.getElementById('__NEXT_DATA__');
                if (nextData) {
                    try {
                        result.__NEXT_DATA__ = JSON.parse(nextData.textContent);
                    } catch (e) {}
                }
                
                // Try __INITIAL_STATE__ - also check for stringified
                if (window.__INITIAL_STATE__) {
                    let is = window.__INITIAL_STATE__;
                    if (typeof is === 'string') {
                        try {
                            result.__INITIAL_STATE__ = JSON.parse(is);
                        } catch (e) {
                            result.__INITIAL_STATE__ = is;
                        }
                    } else {
                        result.__INITIAL_STATE__ = is;
                    }
                }
                
                // Try Apollo Client cache
                if (window.__APOLLO_CLIENT__) {
                    try {
                        result.__APOLLO_CLIENT__ = window.__APOLLO_CLIENT__.extract();
                    } catch (e) {}
                }
                
                return result;
            }
        """)
        
        await context.close()
        
        return {
            "success": True,
            "html": html,
            "state": state_data,
            "url": url
        }
            
    except Exception as e:
        print(f"Browser fetch error for {url}: {e}")
        return {
            "success": False,
            "error": str(e),
            "html": "",
            "state": {}
        }
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


async def extract_products_from_page(url: str, selectors: Dict[str, str]) -> List[Dict]:
    """
    Extract product data directly from DOM elements.
    
    Args:
        url: URL to fetch
        selectors: Dict with CSS selectors for 'container', 'name', 'price', 'mrp', 'url'
    
    Returns:
        List of product dicts
    """
    playwright = None
    browser = None
    
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        await page.goto(url, wait_until="networkidle", timeout=10000)
        
        # Wait for product container
        container = selectors.get("container", ".product-card")
        try:
            await page.wait_for_selector(container, timeout=3000)
        except Exception:
            pass
        
        # Extract products from DOM
        products = await page.evaluate("""
            (selectors) => {
                const container = selectors.container || '.product-card';
                const nameSelector = selectors.name || 'h2, h3, .name';
                const priceSelector = selectors.price || '.price';
                const mrpSelector = selectors.mrp || '.mrp';
                const urlSelector = selectors.url || 'a';
                
                const products = [];
                const items = document.querySelectorAll(container);
                
                items.forEach((item, i) => {
                    if (i >= 5) return;
                    
                    const nameEl = item.querySelector(nameSelector);
                    const priceEl = item.querySelector(priceSelector);
                    const mrpEl = item.querySelector(mrpSelector);
                    const urlEl = item.querySelector(urlSelector);
                    
                    if (nameEl && priceEl) {
                        const priceText = priceEl.textContent || '';
                        const priceMatch = priceText.match(/[\\d,]+\\.?\\d*/);
                        const price = priceMatch ? parseFloat(priceMatch[0].replace(',', '')) : 0;
                        
                        const mrpText = mrpEl ? mrpEl.textContent : '';
                        const mrpMatch = mrpText.match(/[\\d,]+\\.?\\d*/);
                        const mrp = mrpMatch ? parseFloat(mrpMatch[0].replace(',', '')) : 0;
                        
                        products.push({
                            name: nameEl.textContent.trim(),
                            price: price,
                            mrp: mrp || price,
                            url: urlEl ? urlEl.href : ''
                        });
                    }
                });
                
                return products;
            }
        """, selectors)
        
        await context.close()
        return products
            
    except Exception as e:
        print(f"DOM extraction error for {url}: {e}")
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
