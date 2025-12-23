"""
Find correct API endpoints for Netmeds and Truemeds
"""
import asyncio
import aiohttp

async def find_netmeds_api():
    print("\n=== NETMEDS API DISCOVERY ===")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.netmeds.com/",
    }
    
    # List of potential API endpoints
    endpoints = [
        ("autocomplete", "https://www.netmeds.com/apiv2/search/search-autocomplete?q=paracetamol&pageNo=1"),
        ("catalog", "https://www.netmeds.com/apiv2/categories/catalogsearch?q=paracetamol"),
        ("search-v2", "https://www.netmeds.com/apiv2/search?q=paracetamol"),
        ("search", "https://www.netmeds.com/api/search?q=paracetamol"),
        ("suggest", "https://www.netmeds.com/api/suggest?q=paracetamol"),
    ]
    
    async with aiohttp.ClientSession() as session:
        for name, url in endpoints:
            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    print(f"{name}: status={response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"  Keys: {list(data.keys())[:5] if isinstance(data, dict) else 'list'}")
                        if isinstance(data, dict) and 'payLoad' in data:
                            payload = data['payLoad']
                            print(f"  Payload keys: {list(payload.keys())[:5] if isinstance(payload, dict) else 'list'}")
            except Exception as e:
                print(f"{name}: error={str(e)[:50]}")


async def find_truemeds_api():
    print("\n=== TRUEMEDS API DISCOVERY ===")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.truemeds.in/",
    }
    
    # List of potential API endpoints
    endpoints = [
        ("search", "https://www.truemeds.in/api/search?q=paracetamol"),
        ("search-v1", "https://www.truemeds.in/api/v1/search?q=paracetamol"),
        ("search-v2", "https://www.truemeds.in/api/v2/search?q=paracetamol"),
        ("products-search", "https://www.truemeds.in/api/products/search?q=paracetamol"),
        ("suggest", "https://www.truemeds.in/api/search/suggest?q=paracetamol"),
        ("autocomplete", "https://www.truemeds.in/api/autocomplete?q=paracetamol"),
    ]
    
    async with aiohttp.ClientSession() as session:
        for name, url in endpoints:
            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    print(f"{name}: status={response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"  Keys: {list(data.keys())[:5] if isinstance(data, dict) else 'list'}")
            except Exception as e:
                print(f"{name}: error={str(e)[:50]}")


async def main():
    await find_netmeds_api()
    await find_truemeds_api()

if __name__ == "__main__":
    asyncio.run(main())
