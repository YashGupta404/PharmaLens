"""
Medicine Knowledge Base using ChromaDB

This module provides a local vector database of medicine names
for the AI agents to search and verify medicine identification.
"""

from typing import List, Dict, Optional
import os

# Common Indian medicines with their generic names and uses
# This is a small seed dataset - in production, this would be loaded from a larger source
MEDICINE_KNOWLEDGE = [
    # Pain/Fever
    {"name": "Dolo 650", "generic": "Paracetamol 650mg", "category": "analgesic", "uses": "fever, pain, headache"},
    {"name": "Crocin 650", "generic": "Paracetamol 650mg", "category": "analgesic", "uses": "fever, pain"},
    {"name": "Calpol 500", "generic": "Paracetamol 500mg", "category": "analgesic", "uses": "fever, mild pain"},
    {"name": "Combiflam", "generic": "Ibuprofen + Paracetamol", "category": "analgesic", "uses": "pain, inflammation, fever"},
    {"name": "Brufen 400", "generic": "Ibuprofen 400mg", "category": "NSAID", "uses": "pain, inflammation"},
    {"name": "Saridon", "generic": "Propyphenazone + Paracetamol + Caffeine", "category": "analgesic", "uses": "headache, migraine"},
    
    # Stomach/Gastric
    {"name": "Pantocid 40", "generic": "Pantoprazole 40mg", "category": "PPI", "uses": "acidity, GERD, ulcer"},
    {"name": "Pantocid DSR", "generic": "Pantoprazole + Domperidone", "category": "PPI", "uses": "acidity, bloating"},
    {"name": "Pan D", "generic": "Pantoprazole + Domperidone", "category": "PPI", "uses": "acidity, nausea"},
    {"name": "Omez 20", "generic": "Omeprazole 20mg", "category": "PPI", "uses": "acidity, ulcer"},
    {"name": "Ranitidine", "generic": "Ranitidine 150mg", "category": "H2 blocker", "uses": "acidity, heartburn"},
    {"name": "Gelusil MPS", "generic": "Aluminium + Magnesium Hydroxide", "category": "antacid", "uses": "acidity, indigestion"},
    {"name": "Digene", "generic": "Aluminium + Magnesium", "category": "antacid", "uses": "acidity, gas"},
    
    # Antibiotics
    {"name": "Azithral 500", "generic": "Azithromycin 500mg", "category": "antibiotic", "uses": "bacterial infections"},
    {"name": "Augmentin 625", "generic": "Amoxicillin + Clavulanic Acid", "category": "antibiotic", "uses": "bacterial infections"},
    {"name": "Ciprofloxacin 500", "generic": "Ciprofloxacin 500mg", "category": "antibiotic", "uses": "UTI, bacterial infections"},
    {"name": "Cefixime 200", "generic": "Cefixime 200mg", "category": "antibiotic", "uses": "respiratory, UTI infections"},
    
    # Anti-inflammatory
    {"name": "Nucoxia 90", "generic": "Etoricoxib 90mg", "category": "NSAID", "uses": "arthritis, joint pain"},
    {"name": "Nucoxia 60", "generic": "Etoricoxib 60mg", "category": "NSAID", "uses": "pain, inflammation"},
    {"name": "Hifenac P", "generic": "Aceclofenac + Paracetamol", "category": "NSAID", "uses": "pain, swelling"},
    {"name": "Zerodol SP", "generic": "Aceclofenac + Paracetamol + Serratiopeptidase", "category": "NSAID", "uses": "pain, swelling, inflammation"},
    
    # Diabetes
    {"name": "Metformin 500", "generic": "Metformin 500mg", "category": "antidiabetic", "uses": "type 2 diabetes"},
    {"name": "Glycomet 500", "generic": "Metformin 500mg", "category": "antidiabetic", "uses": "diabetes"},
    {"name": "Glimepiride 1mg", "generic": "Glimepiride 1mg", "category": "antidiabetic", "uses": "diabetes"},
    
    # Blood Pressure
    {"name": "Amlodipine 5", "generic": "Amlodipine 5mg", "category": "antihypertensive", "uses": "high BP"},
    {"name": "Telmisartan 40", "generic": "Telmisartan 40mg", "category": "ARB", "uses": "hypertension"},
    {"name": "Atenolol 50", "generic": "Atenolol 50mg", "category": "beta blocker", "uses": "high BP, heart rate"},
    
    # Vitamins/Supplements
    {"name": "Becosules", "generic": "Vitamin B Complex", "category": "vitamin", "uses": "vitamin deficiency"},
    {"name": "Limcee", "generic": "Vitamin C 500mg", "category": "vitamin", "uses": "immunity, vitamin C deficiency"},
    {"name": "Shelcal 500", "generic": "Calcium + Vitamin D3", "category": "supplement", "uses": "calcium deficiency, bones"},
    {"name": "Zincovit", "generic": "Multivitamins + Zinc", "category": "vitamin", "uses": "general wellness"},
    
    # Allergy
    {"name": "Cetirizine 10", "generic": "Cetirizine 10mg", "category": "antihistamine", "uses": "allergy, cold"},
    {"name": "Allegra 120", "generic": "Fexofenadine 120mg", "category": "antihistamine", "uses": "allergy, hives"},
    {"name": "Montair LC", "generic": "Montelukast + Levocetirizine", "category": "antiallergic", "uses": "asthma, allergy"},
    
    # Others
    {"name": "HCQS 200", "generic": "Hydroxychloroquine 200mg", "category": "antimalarial", "uses": "rheumatoid arthritis, lupus"},
    {"name": "HCQS 400", "generic": "Hydroxychloroquine 400mg", "category": "antimalarial", "uses": "rheumatoid arthritis"},
    {"name": "Aspirin 75", "generic": "Aspirin 75mg", "category": "antiplatelet", "uses": "heart protection"},
    {"name": "Ecosprin 75", "generic": "Aspirin 75mg", "category": "antiplatelet", "uses": "heart protection"},
]


class MedicineKnowledgeBase:
    """
    Simple medicine knowledge base using in-memory search.
    In production, this would use ChromaDB for vector similarity search.
    """
    
    def __init__(self):
        self.medicines = MEDICINE_KNOWLEDGE
        self._index = self._build_index()
    
    def _build_index(self) -> Dict[str, Dict]:
        """Build a search index for quick lookups."""
        index = {}
        for med in self.medicines:
            # Index by lowercase name
            name_lower = med["name"].lower()
            index[name_lower] = med
            
            # Also index common variations
            words = name_lower.split()
            if words:
                index[words[0]] = med
        return index
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for medicines matching the query.
        Uses simple string matching (production would use vector similarity).
        """
        query_lower = query.lower().strip()
        results = []
        
        # Exact match
        if query_lower in self._index:
            results.append(self._index[query_lower])
        
        # Partial match
        for med in self.medicines:
            if med not in results:
                name_lower = med["name"].lower()
                generic_lower = med["generic"].lower()
                
                if query_lower in name_lower or query_lower in generic_lower:
                    results.append(med)
                elif any(word in query_lower for word in name_lower.split()):
                    results.append(med)
        
        return results[:top_k]
    
    def identify_medicine(self, ocr_text: str) -> List[Dict]:
        """
        Try to identify medicines from garbled OCR text.
        Uses fuzzy matching to handle OCR errors.
        """
        ocr_lower = ocr_text.lower()
        identified = []
        
        for med in self.medicines:
            name_lower = med["name"].lower()
            name_parts = name_lower.replace("-", " ").split()
            
            # Check if any significant part of medicine name is in OCR text
            for part in name_parts:
                if len(part) >= 3 and part in ocr_lower:
                    identified.append({
                        **med,
                        "confidence": 0.8,
                        "matched_on": part
                    })
                    break
        
        return identified
    
    def get_similar_names(self, misspelled: str) -> List[str]:
        """
        Find medicines with similar names (for OCR error correction).
        """
        misspelled_lower = misspelled.lower()
        suggestions = []
        
        for med in self.medicines:
            name = med["name"]
            name_lower = name.lower()
            
            # Simple similarity: shared characters
            shared = sum(1 for c in misspelled_lower if c in name_lower)
            similarity = shared / max(len(misspelled_lower), len(name_lower))
            
            if similarity > 0.5:
                suggestions.append({"name": name, "similarity": similarity})
        
        suggestions.sort(key=lambda x: x["similarity"], reverse=True)
        return [s["name"] for s in suggestions[:5]]


# Singleton instance
_knowledge_base = None


def get_knowledge_base() -> MedicineKnowledgeBase:
    """Get or create the medicine knowledge base instance."""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = MedicineKnowledgeBase()
    return _knowledge_base
