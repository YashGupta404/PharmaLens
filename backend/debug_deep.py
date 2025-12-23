"""
Deep debug to find correct JSON paths in pharmacy responses.
"""

import asyncio
import httpx
import json
import re

def find_products_in_dict(d, path="", depth=0, max_depth=5):
    """Recursively find arrays that look like product lists."""
    if depth > max_depth:
        return []
    
    results = []
    
    if isinstance(d, dict):
        for key, value in d.items():
            current_path = f"{path}.{key}" if path else key
            
            # Check if this is a products array
            if isinstance(value, list) and len(value) > 0:
                first_item = value[0]
                if isinstance(first_item, dict):
                    # Check if it looks like a product (has name/price keys)
                    keys = set(first_item.keys())
                    product_indicators = {'name', 'price', 'salePrice', 'mrp', 'productName', 'slug'}
                    if keys & product_indicators:
                        results.append({
                            "path": current_path,
                            "count": len(value),
                            "sample_keys": list(first_item.keys())[:10],
                            "sample_name": first_item.get('name') or first_item.get('productName'),
                            "sample_price": first_item.get('price') or first_item.get('salePrice') or first_item.get('mrp')
                        })
            
            # Recurse
            results.extend(find_products_in_dict(value, current_path, depth + 1, max_depth))
    
    elif isinstance(d, list):
        for i, item in enumerate(d[:3]):  # Only first 3 items
            results.extend(find_products_in_dict(item, f"{path}[{i}]", depth + 1, max_depth))
    
    return results

async def deep_debug():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
        
        # Test PharmEasy
        print("\n" + "="*70)
        print("PHARMEASY - Finding products in __NEXT_DATA__")
        print("="*70)
        try:
            url = "https://pharmeasy.in/search/all?name=Nucoxia%2090"
            response = await client.get(url)
            
            match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', response.text, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                
                # Find products
                products_found = find_products_in_dict(data)
                
                if products_found:
                    print(f"Found {len(products_found)} potential product arrays:")
                    for p in products_found[:5]:
                        print(f"\n  Path: {p['path']}")
                        print(f"  Count: {p['count']} items")
                        print(f"  Sample name: {p['sample_name']}")
                        print(f"  Sample price: {p['sample_price']}")
                        print(f"  Keys: {p['sample_keys']}")
                else:
                    # Print top-level structure
                    print("No product arrays found. Top-level keys:")
                    props = data.get("props", {})
                    page_props = props.get("pageProps", {})
                    print(f"  pageProps keys: {list(page_props.keys())[:10]}")
                    
                    # Try searching key by key
                    for key in page_props.keys():
                        val = page_props[key]
                        if isinstance(val, dict):
                            print(f"  {key} (dict): {list(val.keys())[:5]}")
                        elif isinstance(val, list):
                            print(f"  {key} (list): {len(val)} items")
                        else:
                            print(f"  {key}: {type(val).__name__}")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 1mg
        print("\n" + "="*70)
        print("1MG - Finding products in __NEXT_DATA__")
        print("="*70)
        try:
            url = "https://www.1mg.com/search/all?name=Nucoxia%2090"
            response = await client.get(url)
            
            match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', response.text, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                products_found = find_products_in_dict(data)
                
                if products_found:
                    print(f"Found {len(products_found)} potential product arrays:")
                    for p in products_found[:5]:
                        print(f"\n  Path: {p['path']}")
                        print(f"  Count: {p['count']} items")
                        print(f"  Sample name: {p['sample_name']}")
                        print(f"  Sample price: {p['sample_price']}")
                else:
                    props = data.get("props", {})
                    page_props = props.get("pageProps", {})
                    print(f"pageProps keys: {list(page_props.keys())[:10]}")
            else:
                print("No __NEXT_DATA__ found")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(deep_debug())
