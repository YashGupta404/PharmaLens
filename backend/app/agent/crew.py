"""
CrewAI Multi-Agent System for PharmaLens

This module implements a multi-agent system using CrewAI concepts.
Three agents work together:
1. OCR Interpreter Agent - Fixes OCR errors in handwritten text
2. Medicine Identifier Agent - Identifies medicines from text
3. Price Finder Agent - Searches pharmacies for best prices

Note: Using simplified custom implementation for compatibility.
Production would use full CrewAI library.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
import time

from app.agent.knowledge_base import get_knowledge_base
from app.services.scrapers import (
    PharmEasyScraper, OneMgScraper, NetmedsScraper, ApolloScraper
)


class AgentStatus(Enum):
    """Status of an agent."""
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentUpdate:
    """Real-time update from an agent."""
    agent_name: str
    status: AgentStatus
    message: str
    progress: int  # 0-100
    timestamp: float
    data: Optional[Dict] = None


class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, name: str, role: str, goal: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.status = AgentStatus.IDLE
        self._on_update: Optional[Callable] = None
    
    def set_update_callback(self, callback: Callable):
        """Set callback for status updates."""
        self._on_update = callback
    
    def _emit_update(self, message: str, progress: int, data: Dict = None):
        """Emit a status update."""
        if self._on_update:
            update = AgentUpdate(
                agent_name=self.name,
                status=self.status,
                message=message,
                progress=progress,
                timestamp=time.time(),
                data=data
            )
            self._on_update(update)
    
    async def execute(self, input_data: Any) -> Dict[str, Any]:
        """Execute the agent's task. Override in subclasses."""
        raise NotImplementedError


class OCRInterpreterAgent(BaseAgent):
    """
    Agent 1: OCR Interpreter
    Takes raw OCR text and attempts to fix common errors.
    """
    
    def __init__(self):
        super().__init__(
            name="OCR Interpreter",
            role="Text Interpreter",
            goal="Fix OCR errors and clean up prescription text"
        )
        self.knowledge_base = get_knowledge_base()
    
    async def execute(self, ocr_text: str) -> Dict[str, Any]:
        """Interpret and fix OCR text."""
        self.status = AgentStatus.WORKING
        self._emit_update("Analyzing OCR text...", 10)
        
        try:
            await asyncio.sleep(0.5)  # Simulate processing
            
            self._emit_update("Identifying potential medicine names...", 30)
            
            # Split text into lines/words
            lines = ocr_text.strip().split('\n')
            potential_meds = []
            
            for line in lines:
                words = line.strip().split()
                for word in words:
                    if len(word) >= 3:
                        # Check if word might be a medicine
                        suggestions = self.knowledge_base.get_similar_names(word)
                        if suggestions:
                            potential_meds.append({
                                "original": word,
                                "suggestions": suggestions[:3]
                            })
            
            self._emit_update("Correcting spelling errors...", 60)
            await asyncio.sleep(0.3)
            
            # Build corrected text
            corrected_items = []
            for item in potential_meds:
                if item["suggestions"]:
                    corrected_items.append(item["suggestions"][0])
            
            self._emit_update("OCR interpretation complete!", 100)
            self.status = AgentStatus.COMPLETED
            
            return {
                "success": True,
                "original_text": ocr_text,
                "potential_medicines": potential_meds,
                "corrected_names": corrected_items,
                "agent": self.name
            }
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self._emit_update(f"Error: {str(e)}", 0)
            return {"success": False, "error": str(e), "agent": self.name}


class MedicineIdentifierAgent(BaseAgent):
    """
    Agent 2: Medicine Identifier
    Uses knowledge base to identify and verify medicines.
    """
    
    def __init__(self):
        super().__init__(
            name="Medicine Identifier",
            role="Medicine Expert",
            goal="Identify and verify medicine names from prescription"
        )
        self.knowledge_base = get_knowledge_base()
    
    async def execute(self, input_data: Dict) -> Dict[str, Any]:
        """Identify medicines from OCR interpreter output."""
        self.status = AgentStatus.WORKING
        self._emit_update("Searching medicine knowledge base...", 10)
        
        try:
            corrected_names = input_data.get("corrected_names", [])
            original_text = input_data.get("original_text", "")
            
            await asyncio.sleep(0.5)
            
            self._emit_update("Cross-referencing with medical database...", 30)
            
            identified_medicines = []
            
            # Search knowledge base for each potential medicine
            for name in corrected_names:
                results = self.knowledge_base.search(name, top_k=1)
                if results:
                    med = results[0]
                    identified_medicines.append({
                        "name": med["name"],
                        "generic": med["generic"],
                        "category": med["category"],
                        "uses": med["uses"],
                        "confidence": 0.85
                    })
            
            self._emit_update("Analyzing prescription context...", 60)
            await asyncio.sleep(0.3)
            
            # Also try to identify from original text
            direct_matches = self.knowledge_base.identify_medicine(original_text)
            for match in direct_matches:
                if not any(m["name"] == match["name"] for m in identified_medicines):
                    identified_medicines.append({
                        "name": match["name"],
                        "generic": match["generic"],
                        "category": match["category"],
                        "uses": match["uses"],
                        "confidence": match["confidence"]
                    })
            
            self._emit_update(f"Identified {len(identified_medicines)} medicines!", 100)
            self.status = AgentStatus.COMPLETED
            
            return {
                "success": True,
                "medicines": identified_medicines,
                "count": len(identified_medicines),
                "agent": self.name
            }
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self._emit_update(f"Error: {str(e)}", 0)
            return {"success": False, "error": str(e), "agent": self.name}


class PriceFinderAgent(BaseAgent):
    """
    Agent 3: Price Finder
    Searches pharmacies for the best prices.
    """
    
    def __init__(self):
        super().__init__(
            name="Price Finder",
            role="Price Comparison Expert",
            goal="Find the best prices across pharmacies"
        )
    
    async def execute(self, input_data: Dict) -> Dict[str, Any]:
        """Search pharmacies for medicine prices."""
        self.status = AgentStatus.WORKING
        self._emit_update("Initializing pharmacy connections...", 5)
        
        try:
            medicines = input_data.get("medicines", [])
            
            if not medicines:
                self._emit_update("No medicines to search", 100)
                self.status = AgentStatus.COMPLETED
                return {"success": True, "results": [], "agent": self.name}
            
            all_results = []
            total_meds = len(medicines)
            
            scrapers = [
                ("PharmEasy", PharmEasyScraper()),
                ("1mg", OneMgScraper()),
                ("Netmeds", NetmedsScraper()),
                ("Apollo", ApolloScraper()),
            ]
            
            for i, med_info in enumerate(medicines):
                med_name = med_info.get("name", "")
                progress = int((i + 1) / total_meds * 80) + 10
                
                self._emit_update(f"Searching {med_name}...", progress)
                
                med_results = {
                    "medicine": med_name,
                    "generic": med_info.get("generic", ""),
                    "prices": []
                }
                
                for pharmacy_name, scraper in scrapers:
                    try:
                        self._emit_update(f"Checking {pharmacy_name} for {med_name}...", progress)
                        prices = await scraper.search(med_name)
                        if prices:
                            cheapest = min(prices, key=lambda x: x.price)
                            med_results["prices"].append({
                                "pharmacy": pharmacy_name,
                                "price": cheapest.price,
                                "product": cheapest.product_name,
                                "pack_size": cheapest.pack_size,
                            })
                    except Exception:
                        pass
                
                if med_results["prices"]:
                    med_results["prices"].sort(key=lambda x: x["price"])
                    med_results["cheapest"] = med_results["prices"][0]
                    all_results.append(med_results)
            
            self._emit_update(f"Found prices for {len(all_results)} medicines!", 100)
            self.status = AgentStatus.COMPLETED
            
            return {
                "success": True,
                "results": all_results,
                "total_medicines": len(all_results),
                "agent": self.name
            }
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self._emit_update(f"Error: {str(e)}", 0)
            return {"success": False, "error": str(e), "agent": self.name}


class PharmaLensCrew:
    """
    Multi-agent crew for prescription processing.
    Coordinates three agents working together.
    """
    
    def __init__(self):
        self.ocr_agent = OCRInterpreterAgent()
        self.medicine_agent = MedicineIdentifierAgent()
        self.price_agent = PriceFinderAgent()
        self._updates: List[AgentUpdate] = []
        self._on_update: Optional[Callable] = None
    
    def set_update_callback(self, callback: Callable):
        """Set callback for real-time updates."""
        self._on_update = callback
        
        def collect_update(update: AgentUpdate):
            self._updates.append(update)
            if self._on_update:
                self._on_update(update)
        
        self.ocr_agent.set_update_callback(collect_update)
        self.medicine_agent.set_update_callback(collect_update)
        self.price_agent.set_update_callback(collect_update)
    
    async def process_prescription(self, ocr_text: str) -> Dict[str, Any]:
        """
        Run the full crew workflow:
        1. OCR Interpreter fixes text
        2. Medicine Identifier finds medicines
        3. Price Finder searches pharmacies
        """
        self._updates = []
        
        # Step 1: OCR Interpretation
        ocr_result = await self.ocr_agent.execute(ocr_text)
        
        if not ocr_result.get("success"):
            return {"success": False, "error": "OCR interpretation failed", "updates": self._updates}
        
        # Step 2: Medicine Identification
        medicine_result = await self.medicine_agent.execute(ocr_result)
        
        if not medicine_result.get("success"):
            return {"success": False, "error": "Medicine identification failed", "updates": self._updates}
        
        # Step 3: Price Finding (only if medicines were identified)
        if medicine_result.get("medicines"):
            price_result = await self.price_agent.execute(medicine_result)
        else:
            price_result = {"success": True, "results": [], "agent": "Price Finder"}
        
        return {
            "success": True,
            "ocr_interpretation": ocr_result,
            "identified_medicines": medicine_result.get("medicines", []),
            "price_comparison": price_result.get("results", []),
            "updates": [
                {
                    "agent": u.agent_name,
                    "status": u.status.value,
                    "message": u.message,
                    "progress": u.progress
                }
                for u in self._updates
            ]
        }


# Singleton instance
_crew = None


def get_crew() -> PharmaLensCrew:
    """Get or create the PharmaLens crew instance."""
    global _crew
    if _crew is None:
        _crew = PharmaLensCrew()
    return _crew
