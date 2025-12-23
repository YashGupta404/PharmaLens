"""
LangChain Tools for PharmaLens

This module wraps existing scrapers as LangChain tools.
NO MODIFICATIONS to existing scraper code - just wraps them.
"""

from typing import List, Optional
from langchain_core.tools import tool
import asyncio


# Import existing scrapers (NO CHANGES to these)
from app.services.scrapers import (
    PharmEasyScraper,
    OneMgScraper,
    NetmedsScraper,
    ApolloScraper,
)


@tool
def search_pharmeasy(medicine_name: str) -> str:
    """
    Search for medicine prices on PharmEasy pharmacy.
    Use this tool when you need to find medicine prices from PharmEasy.
    
    Args:
        medicine_name: Name of the medicine to search (e.g., "Dolo 650", "Pantocid 40")
    
    Returns:
        JSON string with product names and prices from PharmEasy
    """
    try:
        scraper = PharmEasyScraper()
        results = asyncio.get_event_loop().run_until_complete(scraper.search(medicine_name))
        
        if not results:
            return f"No products found on PharmEasy for '{medicine_name}'"
        
        output = f"PharmEasy results for '{medicine_name}':\n"
        for r in results[:5]:
            output += f"- {r.product_name}: ₹{r.price} ({r.pack_size})\n"
        return output
    except Exception as e:
        return f"PharmEasy search failed: {str(e)}"


@tool
def search_1mg(medicine_name: str) -> str:
    """
    Search for medicine prices on 1mg pharmacy.
    Use this tool when you need to find medicine prices from 1mg/Tata 1mg.
    
    Args:
        medicine_name: Name of the medicine to search (e.g., "Dolo 650", "Crocin")
    
    Returns:
        JSON string with product names and prices from 1mg
    """
    try:
        scraper = OneMgScraper()
        results = asyncio.get_event_loop().run_until_complete(scraper.search(medicine_name))
        
        if not results:
            return f"No products found on 1mg for '{medicine_name}'"
        
        output = f"1mg results for '{medicine_name}':\n"
        for r in results[:5]:
            output += f"- {r.product_name}: ₹{r.price} ({r.pack_size})\n"
        return output
    except Exception as e:
        return f"1mg search failed: {str(e)}"


@tool
def search_netmeds(medicine_name: str) -> str:
    """
    Search for medicine prices on Netmeds pharmacy.
    Use this tool when you need to find medicine prices from Netmeds.
    
    Args:
        medicine_name: Name of the medicine to search
    
    Returns:
        JSON string with product names and prices from Netmeds
    """
    try:
        scraper = NetmedsScraper()
        results = asyncio.get_event_loop().run_until_complete(scraper.search(medicine_name))
        
        if not results:
            return f"No products found on Netmeds for '{medicine_name}'"
        
        output = f"Netmeds results for '{medicine_name}':\n"
        for r in results[:5]:
            output += f"- {r.product_name}: ₹{r.price} ({r.pack_size})\n"
        return output
    except Exception as e:
        return f"Netmeds search failed: {str(e)}"


@tool
def search_apollo(medicine_name: str) -> str:
    """
    Search for medicine prices on Apollo Pharmacy.
    Use this tool when you need to find medicine prices from Apollo.
    
    Args:
        medicine_name: Name of the medicine to search
    
    Returns:
        JSON string with product names and prices from Apollo
    """
    try:
        scraper = ApolloScraper()
        results = asyncio.get_event_loop().run_until_complete(scraper.search(medicine_name))
        
        if not results:
            return f"No products found on Apollo for '{medicine_name}'"
        
        output = f"Apollo results for '{medicine_name}':\n"
        for r in results[:5]:
            output += f"- {r.product_name}: ₹{r.price} ({r.pack_size})\n"
        return output
    except Exception as e:
        return f"Apollo search failed: {str(e)}"


@tool
def compare_prices(medicine_name: str) -> str:
    """
    Search for medicine prices across ALL pharmacies and compare them.
    Use this tool to find the cheapest price for a medicine.
    
    Args:
        medicine_name: Name of the medicine to compare prices for
    
    Returns:
        Comparison of prices across all pharmacies with cheapest option highlighted
    """
    try:
        all_results = []
        scrapers = [
            ("PharmEasy", PharmEasyScraper()),
            ("1mg", OneMgScraper()),
            ("Netmeds", NetmedsScraper()),
            ("Apollo", ApolloScraper()),
        ]
        
        for pharmacy_name, scraper in scrapers:
            try:
                results = asyncio.get_event_loop().run_until_complete(scraper.search(medicine_name))
                if results:
                    cheapest = min(results, key=lambda x: x.price)
                    all_results.append({
                        "pharmacy": pharmacy_name,
                        "product": cheapest.product_name,
                        "price": cheapest.price,
                        "pack_size": cheapest.pack_size,
                    })
            except Exception:
                pass
        
        if not all_results:
            return f"No prices found for '{medicine_name}' on any pharmacy"
        
        # Sort by price
        all_results.sort(key=lambda x: x["price"])
        cheapest = all_results[0]
        
        output = f"Price Comparison for '{medicine_name}':\n\n"
        output += f"🏆 CHEAPEST: {cheapest['pharmacy']} - ₹{cheapest['price']}\n\n"
        output += "All options:\n"
        for r in all_results:
            marker = "✓ " if r == cheapest else "  "
            output += f"{marker}{r['pharmacy']}: ₹{r['price']} ({r['pack_size']})\n"
        
        if len(all_results) > 1:
            savings = all_results[-1]["price"] - all_results[0]["price"]
            output += f"\n💰 Potential savings: ₹{savings:.2f}"
        
        return output
    except Exception as e:
        return f"Price comparison failed: {str(e)}"


# List of all tools for the agent
ALL_TOOLS = [
    search_pharmeasy,
    search_1mg,
    search_netmeds,
    search_apollo,
    compare_prices,
]
