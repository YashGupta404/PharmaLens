"""
Utility Helpers

Common utility functions used across the application.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
import re


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    unique = uuid.uuid4().hex[:12]
    return f"{prefix}_{unique}" if prefix else unique


def generate_prescription_id() -> str:
    """Generate a prescription ID."""
    return generate_id("rx")


def generate_search_id() -> str:
    """Generate a search ID."""
    return generate_id("search")


def sanitize_medicine_name(name: str) -> str:
    """
    Clean and normalize medicine name for search.
    
    - Remove extra whitespace
    - Handle common abbreviations
    - Standardize dosage formats
    """
    # Remove extra whitespace
    name = " ".join(name.split())
    
    # Standardize common patterns
    # e.g., "500 mg" -> "500mg"
    name = re.sub(r'(\d+)\s*(mg|ml|mcg|g)\b', r'\1\2', name, flags=re.IGNORECASE)
    
    return name.strip()


def extract_dosage(medicine_name: str) -> Optional[str]:
    """
    Extract dosage from medicine name.
    
    Examples:
        "Crocin 650mg" -> "650mg"
        "Pan-D 40" -> "40mg"
    """
    pattern = r'(\d+(?:\.\d+)?)\s*(mg|ml|mcg|g|iu)\b'
    match = re.search(pattern, medicine_name, re.IGNORECASE)
    if match:
        return f"{match.group(1)}{match.group(2).lower()}"
    return None


def calculate_savings(prices: List[float]) -> float:
    """
    Calculate potential savings from price list.
    
    Returns difference between highest and lowest price.
    """
    if len(prices) < 2:
        return 0.0
    return max(prices) - min(prices)


def format_currency(amount: float) -> str:
    """Format amount as Indian Rupees."""
    return f"₹{amount:,.2f}"


def parse_pack_size(text: str) -> Dict[str, Any]:
    """
    Parse pack size from text.
    
    Examples:
        "Strip of 15 tablets" -> {"count": 15, "unit": "tablet", "type": "strip"}
        "Bottle of 100ml" -> {"count": 100, "unit": "ml", "type": "bottle"}
    """
    result = {"count": 1, "unit": "piece", "type": "pack"}
    
    # Match patterns like "Strip of 15 tablets"
    pattern = r'(\w+)\s+of\s+(\d+)\s*(\w+)?'
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        result["type"] = match.group(1).lower()
        result["count"] = int(match.group(2))
        if match.group(3):
            result["unit"] = match.group(3).lower().rstrip('s')
    
    return result
