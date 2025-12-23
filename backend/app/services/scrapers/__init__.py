# Scrapers package - 5 Pharmacies
from .base import BaseScraper, ScrapedPrice
from .pharmeasy import PharmEasyScraper
from .onemg import OneMgScraper
from .netmeds import NetmedsScraper
from .apollo import ApolloScraper
from .truemeds import TruemedsScraper

__all__ = [
    "BaseScraper",
    "ScrapedPrice", 
    "PharmEasyScraper",
    "OneMgScraper",
    "NetmedsScraper",
    "ApolloScraper",
    "TruemedsScraper"
]






