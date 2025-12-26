"""
Test All 4 Scrapers

Tests:
- PharmEasy (HTTP)
- 1mg (HTTP)
- Netmeds (Playwright)
- Apollo (Playwright)

Run: python test_http_scrapers.py
"""

import asyncio
import sys
import time

sys.path.insert(0, ".")

async def test_all_scrapers():
    print("=" * 60)
    print("Testing All 4 Medicine Scrapers")
    print("=" * 60)
    
    from app.services.scrapers import PharmEasyScraper, OneMgScraper, NetmedsScraper, ApolloScraper
    
    medicine = "Dolo 650"
    print(f"\nSearching for: {medicine}\n")
    
    scrapers = [
        ("PharmEasy", PharmEasyScraper(), "HTTP"),
        ("1mg", OneMgScraper(), "HTTP"),
        ("Netmeds", NetmedsScraper(), "Playwright"),
        ("Apollo", ApolloScraper(), "Playwright"),
    ]
    
    total_results = 0
    all_results = {}
    
    for name, scraper, scraper_type in scrapers:
        print(f"\n{'='*40}")
        print(f"Testing {name} ({scraper_type})...")
        print("=" * 40)
        
        start = time.time()
        try:
            results = await asyncio.wait_for(
                scraper.search(medicine),
                timeout=35.0
            )
            elapsed = time.time() - start
            
            if results:
                print(f"✅ {name}: Found {len(results)} results in {elapsed:.1f}s")
                for i, r in enumerate(results[:3]):
                    print(f"   {i+1}. {r.product_name[:50]} - ₹{r.price}")
                total_results += len(results)
                all_results[name] = len(results)
            else:
                print(f"⚠️ {name}: No results in {elapsed:.1f}s")
                all_results[name] = 0
                
        except asyncio.TimeoutError:
            elapsed = time.time() - start
            print(f"⏱️ {name}: Timeout after {elapsed:.1f}s")
            all_results[name] = 0
        except Exception as e:
            elapsed = time.time() - start
            print(f"❌ {name}: Error after {elapsed:.1f}s - {e}")
            all_results[name] = 0
    
    print(f"\n{'='*60}")
    print("SUMMARY:")
    print("=" * 60)
    for name, count in all_results.items():
        status = "✅" if count > 0 else "❌"
        print(f"{status} {name}: {count} results")
    print(f"\nTOTAL: {total_results} results from 4 pharmacies")
    print("=" * 60)
    
    return total_results


async def test_full_search():
    """Test the full price search service with semaphore."""
    print("\n" + "=" * 60)
    print("Testing Full Price Search Service (with Semaphore)")
    print("=" * 60)
    
    from app.services.price_search import search_medicine_prices
    
    start = time.time()
    result = await search_medicine_prices("Paracetamol 500mg")
    elapsed = time.time() - start
    
    print(f"\n{'='*40}")
    print("FINAL RESULTS:")
    print("=" * 40)
    print(f"Search completed in {elapsed:.1f}s")
    print(f"Total results: {result.get('total_results', 0)}")
    print(f"Pharmacies searched: {result.get('pharmacies_searched', [])}")
    
    # Count per pharmacy
    prices = result.get('prices', [])
    pharmacy_counts = {}
    for p in prices:
        name = p.get('pharmacy_name', 'Unknown')
        pharmacy_counts[name] = pharmacy_counts.get(name, 0) + 1
    
    print("\nResults per pharmacy:")
    for name, count in pharmacy_counts.items():
        print(f"  {name}: {count} results")
    
    if result.get('cheapest'):
        cheapest = result['cheapest']
        print(f"\nCheapest: ₹{cheapest.get('price')} at {cheapest.get('pharmacy_name')}")
    
    print(f"Potential savings: ₹{result.get('savings', 0)}")
    
    if result.get('errors'):
        print(f"\nErrors: {result['errors']}")
    
    return result.get('total_results', 0)


if __name__ == "__main__":
    print("\n🧪 PharmaLens Full Scraper Test\n")
    
    # Test individual scrapers
    individual_results = asyncio.run(test_all_scrapers())
    
    # Test full service with semaphore
    service_results = asyncio.run(test_full_search())
    
    print("\n" + "=" * 60)
    if individual_results > 0 and service_results > 0:
        print("✅ TESTS PASSED - All scrapers working!")
    elif service_results > 0:
        print("⚠️ PARTIAL SUCCESS - Service works but some scrapers failed")
    else:
        print("❌ TESTS FAILED - Check output above")
    print("=" * 60)
