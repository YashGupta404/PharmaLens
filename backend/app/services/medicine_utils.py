"""
Medicine Name Utilities

Functions to clean, normalize, and extract medicine names for better search results.
Handles variations like:
- "Dolo 650mg tablet" -> "Dolo 650"
- "PARACETAMOL 500MG" -> "Paracetamol 500mg"
- "Crocin Advance (500 mg)" -> "Crocin Advance 500mg"
"""

import re
from typing import Tuple, Optional

# Common medicine forms to strip from names
MEDICINE_FORMS = [
    'tablet', 'tablets', 'tab', 'tabs',
    'capsule', 'capsules', 'cap', 'caps',
    'syrup', 'suspension', 'drops', 'drop',
    'injection', 'inj', 'cream', 'ointment', 'gel',
    'powder', 'sachet', 'strip', 'bottle',
    'ml', 'mg', 'gm', 'g', 'mcg', 'iu',
    'of', 'pack', 'unit', 'units', "'s"
]

# Common brand name mappings (generic to brand alternatives)
MEDICINE_ALTERNATIVES = {
    'paracetamol': ['dolo', 'crocin', 'calpol', 'pacimol', 'pyrigesic'],
    'ibuprofen': ['brufen', 'ibugesic', 'combiflam'],
    'cetirizine': ['cetzine', 'alerid', 'zyrtec', 'okacet'],
    'azithromycin': ['azithral', 'zithromax', 'azee'],
    'amoxicillin': ['mox', 'novamox', 'amoxil'],
    'omeprazole': ['omez', 'ocid', 'omecip'],
    'metformin': ['glycomet', 'glucophage', 'obimet'],
    'atorvastatin': ['atorva', 'lipitor', 'storvas'],
    'pantoprazole': ['pan', 'pantop', 'pantocid'],
    'montelukast': ['montair', 'montek', 'singulair'],
}


def clean_medicine_name(name: str) -> str:
    """
    Clean a medicine name for searching.
    - Normalize case
    - Remove extra whitespace
    - Remove special characters
    - Keep dosage if present
    """
    if not name:
        return ""
    
    # Normalize whitespace and case
    cleaned = " ".join(name.split())
    
    # Remove parentheses but keep content
    cleaned = re.sub(r'\(([^)]+)\)', r' \1 ', cleaned)
    
    # Remove special characters except numbers and basic punctuation
    cleaned = re.sub(r'[^\w\s\.\-]', ' ', cleaned)
    
    # Normalize whitespace again
    cleaned = " ".join(cleaned.split())
    
    return cleaned.strip()


def extract_base_name_and_dosage(medicine_name: str) -> Tuple[str, Optional[str]]:
    """
    Extract the base medicine name and dosage separately.
    
    Examples:
    - "Dolo 650mg" -> ("Dolo", "650mg")
    - "Paracetamol 500 mg tablet" -> ("Paracetamol", "500mg")
    - "Crocin Advance" -> ("Crocin Advance", None)
    """
    cleaned = clean_medicine_name(medicine_name)
    
    # Pattern to match dosage: number followed by mg/ml/g/mcg etc
    dosage_pattern = r'(\d+\.?\d*)\s*(mg|ml|g|gm|mcg|iu|%)'
    
    dosage_match = re.search(dosage_pattern, cleaned, re.IGNORECASE)
    
    if dosage_match:
        dosage = f"{dosage_match.group(1)}{dosage_match.group(2).lower()}"
        # Get the base name (everything before dosage)
        base_name = cleaned[:dosage_match.start()].strip()
        
        # If base name is empty, the whole thing might be after dosage
        if not base_name:
            base_name = cleaned[dosage_match.end():].strip()
        
        # Remove common form words from base name
        words = base_name.split()
        words = [w for w in words if w.lower() not in MEDICINE_FORMS]
        base_name = " ".join(words)
        
        return (base_name.strip(), dosage)
    
    # No dosage found, return cleaned name
    # Remove form words
    words = cleaned.split()
    words = [w for w in words if w.lower() not in MEDICINE_FORMS]
    
    return (" ".join(words).strip(), None)


def get_search_query(medicine_name: str, dosage: Optional[str] = None) -> str:
    """
    Build an optimized search query from medicine name and optional dosage.
    """
    base_name, extracted_dosage = extract_base_name_and_dosage(medicine_name)
    
    # Use provided dosage or extracted one
    final_dosage = dosage or extracted_dosage
    
    if final_dosage:
        return f"{base_name} {final_dosage}".strip()
    
    return base_name.strip()


def get_alternative_names(medicine_name: str) -> list:
    """
    Get alternative brand/generic names for a medicine.
    Useful when exact match isn't found.
    """
    name_lower = medicine_name.lower().strip()
    base_name, _ = extract_base_name_and_dosage(medicine_name)
    base_lower = base_name.lower()
    
    alternatives = []
    
    # Check if it's a generic name with known brands
    for generic, brands in MEDICINE_ALTERNATIVES.items():
        if generic in name_lower or generic in base_lower:
            alternatives.extend(brands)
        # Check if it's a brand name
        for brand in brands:
            if brand in name_lower or brand in base_lower:
                # Add the generic and other brands
                alternatives.append(generic)
                alternatives.extend([b for b in brands if b != brand])
                break
    
    return list(set(alternatives))  # Remove duplicates


def normalize_product_name(product_name: str) -> str:
    """
    Normalize a product name from search results for display.
    """
    if not product_name:
        return ""
    
    # Title case but preserve common abbreviations
    words = product_name.split()
    normalized = []
    
    for word in words:
        # Keep all-caps abbreviations (like "MG", "ML")
        if len(word) <= 3 and word.isupper():
            normalized.append(word)
        else:
            normalized.append(word.capitalize())
    
    return " ".join(normalized)
