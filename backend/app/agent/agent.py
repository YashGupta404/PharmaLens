"""
LangChain Agent for PharmaLens

This module creates an AI agent that can intelligently search for medicine prices
using the available pharmacy tools.

Uses Groq (free tier) as the LLM backend.
Compatible with LangChain 0.2+
"""

from typing import Optional, Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

from app.config import settings


# System prompt for the agent
AGENT_SYSTEM_PROMPT = """You are PharmaLens Agent - an intelligent assistant that helps users find the cheapest medicine prices across Indian online pharmacies.

When a user asks about medicine prices, analyze their query and provide helpful information.
You have access to price data from: PharmEasy, 1mg, Netmeds, and Apollo Pharmacy.

Be helpful, accurate, and always prioritize finding the best deal for the user.
Format prices in Indian Rupees (₹)."""


async def run_agent_query(query: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
    """
    Run a query through the PharmaLens agent.
    
    Args:
        query: User's natural language query (e.g., "Find cheapest Dolo 650")
        chat_history: Optional conversation history
    
    Returns:
        Dict with agent response and metadata
    """
    try:
        # Get API key
        api_key = getattr(settings, 'groq_api_key', None)
        
        if not api_key:
            return {
                "success": False,
                "query": query,
                "error": "Groq API key not found. Set GROQ_API_KEY in .env",
                "agent_type": "langchain_groq",
            }
        
        # Create LLM
        llm = ChatGroq(
            api_key=api_key,
            model="llama-3.3-70b-versatile",
            temperature=0.1,
        )
        
        # Build messages
        messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT)]
        
        # Add chat history if provided
        if chat_history:
            for msg in chat_history:
                if msg.get("role") == "user":
                    messages.append(HumanMessage(content=msg.get("content", "")))
                elif msg.get("role") == "assistant":
                    messages.append(AIMessage(content=msg.get("content", "")))
        
        # Add current query
        messages.append(HumanMessage(content=query))
        
        # Get response
        response = await llm.ainvoke(messages)
        
        return {
            "success": True,
            "query": query,
            "response": response.content,
            "agent_type": "langchain_groq",
        }
        
    except Exception as e:
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "agent_type": "langchain_groq",
        }


async def run_agent_with_tools(medicine_name: str) -> Dict[str, Any]:
    """
    Run agent with pharmacy search tools.
    First searches all pharmacies, then uses LLM to summarize.
    
    Args:
        medicine_name: Medicine to search for
    
    Returns:
        Dict with search results and AI summary
    """
    from app.services.scrapers import (
        PharmEasyScraper, OneMgScraper, NetmedsScraper, ApolloScraper
    )
    
    try:
        # Search all pharmacies
        all_results = []
        scrapers = [
            ("PharmEasy", PharmEasyScraper()),
            ("1mg", OneMgScraper()),
            ("Netmeds", NetmedsScraper()),
            ("Apollo", ApolloScraper()),
        ]
        
        for pharmacy_name, scraper in scrapers:
            try:
                results = await scraper.search(medicine_name)
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
            return {
                "success": False,
                "query": medicine_name,
                "error": f"No prices found for '{medicine_name}'",
                "agent_type": "langchain_tools",
            }
        
        # Sort by price
        all_results.sort(key=lambda x: x["price"])
        cheapest = all_results[0]
        
        # Build summary
        summary = f"🏆 **Best Price for {medicine_name}**\n\n"
        summary += f"**Cheapest:** {cheapest['pharmacy']} - ₹{cheapest['price']:.2f}\n\n"
        summary += "**All Options:**\n"
        for r in all_results:
            marker = "✓" if r == cheapest else " "
            summary += f"{marker} {r['pharmacy']}: ₹{r['price']:.2f} ({r['pack_size']})\n"
        
        if len(all_results) > 1:
            savings = all_results[-1]["price"] - all_results[0]["price"]
            summary += f"\n💰 **Potential savings: ₹{savings:.2f}**"
        
        return {
            "success": True,
            "query": medicine_name,
            "response": summary,
            "prices": all_results,
            "cheapest": cheapest,
            "agent_type": "langchain_tools",
        }
        
    except Exception as e:
        return {
            "success": False,
            "query": medicine_name,
            "error": str(e),
            "agent_type": "langchain_tools",
        }
