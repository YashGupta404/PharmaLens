"""
Debug script to see raw responses from pharmacy sites.
"""

import asyncio
import httpx

async def debug_scrapers():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
        
        # Test PharmEasy
        print("\n=== PHARMEASY ===")
        try:
            url = "https://pharmeasy.in/search/all?name=Nucoxia%2090"
            response = await client.get(url)
            print(f"Status: {response.status_code}")
            print(f"Content length: {len(response.text)} chars")
            
            # Check for __NEXT_DATA__
            if "__NEXT_DATA__" in response.text:
                print("✓ Found __NEXT_DATA__")
                import re
                match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', response.text, re.DOTALL)
                if match:
                    import json
                    data = json.loads(match.group(1))
                    page_props = data.get("props", {}).get("pageProps", {})
                    products = page_props.get("productListing", {}).get("products", [])
                    print(f"  Products found: {len(products)}")
                    if products:
                        p = products[0]
                        print(f"  First product: {p.get('name')} - ₹{p.get('salePrice')}")
            else:
                print("✗ No __NEXT_DATA__ found")
                print(f"First 500 chars: {response.text[:500]}")
        except Exception as e:
            print(f"ERROR: {e}")
        
        # Test 1mg
        print("\n=== 1MG ===")
        try:
            url = "https://www.1mg.com/search/all?name=Nucoxia%2090"
            response = await client.get(url)
            print(f"Status: {response.status_code}")
            print(f"Content length: {len(response.text)} chars")
            
            if "__NEXT_DATA__" in response.text:
                print("✓ Found __NEXT_DATA__")
                import re
                match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', response.text, re.DOTALL)
                if match:
                    import json
                    data = json.loads(match.group(1))
                    skus = data.get("props", {}).get("pageProps", {}).get("searchData", {}).get("skus", [])
                    print(f"  SKUs found: {len(skus)}")
                    if skus:
                        s = skus[0]
                        print(f"  First product: {s.get('name')} - ₹{s.get('price')}")
            else:
                print("✗ No __NEXT_DATA__ found")
                print(f"First 500 chars: {response.text[:500]}")
        except Exception as e:
            print(f"ERROR: {e}")
        
        # Test Netmeds
        print("\n=== NETMEDS ===")
        try:
            url = "https://www.netmeds.com/catalogsearch/result?q=Nucoxia%2090"
            response = await client.get(url)
            print(f"Status: {response.status_code}")
            print(f"Content length: {len(response.text)} chars")
            
            if "__PRELOADED_STATE__" in response.text:
                print("✓ Found __PRELOADED_STATE__")
            else:
                print("✗ No __PRELOADED_STATE__ found")
                # Check for other patterns
                if "product" in response.text.lower():
                    print("  'product' keyword found in response")
                print(f"First 500 chars: {response.text[:500]}")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(debug_scrapers())
