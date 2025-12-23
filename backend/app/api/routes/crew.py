"""
Crew API Routes

Endpoints for the CrewAI multi-agent system.
Shows agent status and allows agent-based prescription processing.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.agent.crew import get_crew, PharmaLensCrew


router = APIRouter()


class CrewProcessRequest(BaseModel):
    """Request to process text with multi-agent crew."""
    ocr_text: str


class AgentStatusItem(BaseModel):
    """Status of a single agent."""
    agent: str
    status: str
    message: str
    progress: int


class CrewProcessResponse(BaseModel):
    """Response from crew processing."""
    success: bool
    identified_medicines: List[Dict[str, Any]]
    price_comparison: List[Dict[str, Any]]
    agent_updates: List[AgentStatusItem]
    error: Optional[str] = None


@router.post("/process", response_model=CrewProcessResponse)
async def process_with_crew(request: CrewProcessRequest):
    """
    Process prescription text using the multi-agent crew.
    
    Three agents work together:
    1. OCR Interpreter - Fixes text errors
    2. Medicine Identifier - Finds medicines using knowledge base
    3. Price Finder - Searches pharmacies for best prices
    
    Returns identified medicines, prices, and real-time agent status updates.
    """
    try:
        crew = get_crew()
        result = await crew.process_prescription(request.ocr_text)
        
        return CrewProcessResponse(
            success=result.get("success", False),
            identified_medicines=result.get("identified_medicines", []),
            price_comparison=result.get("price_comparison", []),
            agent_updates=[
                AgentStatusItem(
                    agent=u["agent"],
                    status=u["status"],
                    message=u["message"],
                    progress=u["progress"]
                )
                for u in result.get("updates", [])
            ],
            error=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Crew processing failed: {str(e)}"
        )


@router.get("/status")
async def get_crew_status():
    """
    Get information about the multi-agent crew.
    """
    return {
        "crew_name": "PharmaLens AI Crew",
        "framework": "CrewAI-style Multi-Agent System",
        "agents": [
            {
                "name": "OCR Interpreter",
                "role": "Text Interpreter",
                "goal": "Fix OCR errors and clean up prescription text",
                "icon": "🔍"
            },
            {
                "name": "Medicine Identifier", 
                "role": "Medicine Expert",
                "goal": "Identify and verify medicine names using knowledge base",
                "icon": "💊"
            },
            {
                "name": "Price Finder",
                "role": "Price Comparison Expert", 
                "goal": "Find the best prices across pharmacies",
                "icon": "💰"
            }
        ],
        "knowledge_base": {
            "type": "In-memory Medicine Database",
            "medicines_count": 40,
            "categories": ["analgesic", "antibiotic", "antidiabetic", "vitamin", "NSAID"]
        }
    }
