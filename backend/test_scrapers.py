"""Test 4 scrapers sequentially for cleaner output"""
import asyncio
import sys
sys.path.insert(0, '.')

async def test_scrapers():
    from app.services.scrapers import PharmEasyScraper, OneMgScraper, NetmedsScraper, ApolloScraper
    
    medicine = "Nucoxia 90"
    print(f"\nTesting for: {medicine}")
    print("="*50)
    
    scrapers = [
        ("PharmEasy", PharmEasyScraper()),
        ("1mg", OneMgScraper()),
        ("Netmeds", NetmedsScraper()),
        ("Apollo", ApolloScraper()),
    ]
    
    for name, scraper in scrapers:
        try:
            results = await scraper.search(medicine)
            print(f"\n{name}: {len(results)} results")
            for r in results[:2]:
                mrp = f" (MRP: {r.original_price})" if r.original_price else ""
                print(f"  - {r.product_name[:35]}: Rs.{r.price}{mrp}")
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
        finally:
            await scraper.close()
    
    print("\n" + "="*50)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(test_scrapers())
