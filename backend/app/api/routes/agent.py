"""
Agent API Routes

NEW endpoints for LangChain agent-based search.
These are SEPARATE from existing search endpoints - nothing is modified.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.agent.agent import run_agent_query, run_agent_with_tools


router = APIRouter()


class AgentQueryRequest(BaseModel):
    """Request body for agent query."""
    query: str
    chat_history: Optional[List[Dict[str, str]]] = None


class AgentSearchRequest(BaseModel):
    """Request body for agent tool search."""
    medicine_name: str


class AgentQueryResponse(BaseModel):
    """Response from agent query."""
    success: bool
    query: str
    response: str
    agent_type: str
    error: Optional[str] = None


class AgentSearchResponse(BaseModel):
    """Response from agent tool search."""
    success: bool
    query: str
    response: str
    agent_type: str
    prices: Optional[List[Dict[str, Any]]] = None
    cheapest: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/chat", response_model=AgentQueryResponse)
async def agent_chat(request: AgentQueryRequest):
    """
    Chat with PharmaLens AI Agent using natural language.
    
    Example queries:
    - "What is Dolo 650 used for?"
    - "Tell me about Pantoprazole"
    """
    try:
        result = await run_agent_query(
            query=request.query,
            chat_history=request.chat_history
        )
        
        return AgentQueryResponse(
            success=result.get("success", False),
            query=result.get("query", request.query),
            response=result.get("response", ""),
            agent_type=result.get("agent_type", "langchain"),
            error=result.get("error"),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent query failed: {str(e)}"
        )


@router.post("/search", response_model=AgentSearchResponse)
async def agent_search(request: AgentSearchRequest):
    """
    Search for medicine prices using LangChain AI Agent with tools.
    
    The agent will:
    1. Search all pharmacies (PharmEasy, 1mg, Netmeds, Apollo)
    2. Compare prices and find the cheapest option
    3. Return structured results with AI summary
    
    This is a NEW endpoint - the original /search/medicine endpoint is unchanged.
    """
    try:
        result = await run_agent_with_tools(medicine_name=request.medicine_name)
        
        return AgentSearchResponse(
            success=result.get("success", False),
            query=result.get("query", request.medicine_name),
            response=result.get("response", ""),
            agent_type=result.get("agent_type", "langchain_tools"),
            prices=result.get("prices"),
            cheapest=result.get("cheapest"),
            error=result.get("error"),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent search failed: {str(e)}"
        )


@router.get("/info")
async def agent_info():
    """
    Get information about the PharmaLens AI Agent.
    """
    return {
        "agent_name": "PharmaLens Agent",
        "description": "AI-powered medicine price comparison using LangChain",
        "llm": "Groq (llama-3.3-70b-versatile)",
        "tools": [
            {
                "name": "search_pharmeasy",
                "description": "Search PharmEasy pharmacy"
            },
            {
                "name": "search_1mg",
                "description": "Search 1mg/Tata 1mg pharmacy"
            },
            {
                "name": "search_netmeds",
                "description": "Search Netmeds pharmacy"
            },
            {
                "name": "search_apollo",
                "description": "Search Apollo Pharmacy"
            },
        ],
        "endpoints": {
            "/api/agent/search": "Search with AI agent + pharmacy tools",
            "/api/agent/chat": "Natural language chat with AI",
            "/api/agent/info": "Agent information",
        },
        "example_queries": [
            "Dolo 650",
            "Pantocid 40",
            "Crocin 500",
        ]
    }
