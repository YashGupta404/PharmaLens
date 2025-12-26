# Scrapers package - 4 Pharmacies
# PharmEasy + 1mg: HTTP (fast, low memory)
# Netmeds + Apollo: Playwright (one at a time for memory efficiency)

from .base import BaseScraper, ScrapedPrice
from .pharmeasy import PharmEasyScraper
from .onemg_http import OneMgScraper  # HTTP version - fast
from .netmeds import NetmedsScraper   # Playwright version - works
from .apollo import ApolloScraper     # Playwright version - works

__all__ = [
    "BaseScraper",
    "ScrapedPrice", 
    "PharmEasyScraper",
    "OneMgScraper",
    "NetmedsScraper",
    "ApolloScraper",
]
