"""
Test streaming search
"""
import asyncio
from app.services.price_search import search_medicine_prices_stream


async def test_stream():
    print("Starting streaming search for 'paracetamol'...")
    print("=" * 50)
    
    async for event in search_medicine_prices_stream("paracetamol"):
        event_type = event.get("type", "unknown")
        
        if event_type == "started":
            print(f"[STARTED] {event.get('message', '')}")
            print(f"  Pharmacies: {event.get('pharmacies', [])}")
        
        elif event_type == "pharmacy_result":
            pharmacy = event.get("pharmacy", "Unknown")
            results_count = event.get("results_count", 0)
            completed = event.get("completed", 0)
            remaining = event.get("remaining", 0)
            print(f"[PHARMACY] {pharmacy}: {results_count} results")
            print(f"  Progress: {completed}/5 done, {remaining} remaining")
            print(f"  Message: {event.get('message', '')}")
        
        elif event_type == "complete":
            print(f"\n[COMPLETE] {event.get('message', '')}")
            print(f"  Total results: {event.get('total_results', 0)}")
            print(f"  Completed pharmacies: {event.get('completed_pharmacies', [])}")
            if event.get("cheapest"):
                cheapest = event.get("cheapest")
                print(f"  Cheapest: ₹{cheapest.get('price', 0)} at {cheapest.get('pharmacy_name', 'Unknown')}")
            print(f"  Savings: ₹{event.get('savings', 0)}")
        
        elif event_type == "error":
            print(f"[ERROR] {event.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 50)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(test_stream())
