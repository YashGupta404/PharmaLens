"""
AI Parser Service

Uses Groq (free) with Llama models for medicine extraction from prescription text.
CRITICAL: This is for medical purposes - accuracy is paramount!
"""

import httpx
from typing import List, Optional, Dict, Any
import json
import re

from app.config import settings


# Pydantic models for extracted data
from pydantic import BaseModel


class ExtractedMedicine(BaseModel):
    """Extracted medicine from prescription."""
    name: str
    dosage: str = ""
    frequency: str = ""
    quantity: int = 0
    duration: str = ""
    generic_name: str = ""
    is_generic: bool = False
    form: str = ""  # tablet, capsule, syrup, spray, etc.


# Groq API configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def get_groq_headers():
    """Get headers for Groq API calls."""
    api_key = settings.groq_api_key if hasattr(settings, 'groq_api_key') else ""
    
    if not api_key:
        # Fallback to gemini key name or explicit groq key
        api_key = getattr(settings, 'gemini_api_key', '') or ""
    
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


# INTELLIGENT Prompt that INTERPRETS OCR text, not just extracts literally
MEDICINE_EXTRACTION_PROMPT = """You are an EXPERT Indian pharmacist and prescription interpreter with 20+ years of experience.

YOUR TASK: Analyze messy OCR text from a handwritten Indian prescription and INTELLIGENTLY IDENTIFY ALL MEDICINES.

⚠️ CRITICAL: OCR from handwriting is OFTEN WRONG! You must:
1. INTERPRET the text, not just extract literally
2. CORRECT common OCR errors (e.g., "PANTCID" → "Pantocid", "Hexar" → "HCQS", "Nucoxla" → "Nucoxia")
3. USE MEDICAL CONTEXT to understand what the prescription is for
4. PREDICT what medicines a doctor would typically prescribe based on symptoms/conditions mentioned

COMMON OCR MISTAKES TO FIX:
- "PANTCID", "PANTOCLD", "PANTO CID" → Pantocid (Pantoprazole)
- "HCQS", "Hexar", "HCQZ" → HCQS (Hydroxychloroquine)
- "Nucoxla", "Nucoxio", "Nucoxea" → Nucoxia (Etoricoxib)
- "Rabitex", "Rabltex", "Rabitax" → Rabitex DSR (Rabeprazole+Domperidone)
- "Dolo", "D0L0", "DOL0" → Dolo (Paracetamol)
- "Pan D", "PAN-D", "PAND" → Pan-D (Pantoprazole+Domperidone)
- "Limcee", "Llmcee" → Limcee (Vitamin C)
- "Shelcal", "Shel cal" → Shelcal (Calcium)
- Numbers like "40", "500", "650" usually indicate DOSAGE in mg

INDIAN PRESCRIPTION PATTERNS:
- Row 1, Row 2, etc. with medicine names = Prescription table format
- "Rx" followed by medicines = Standard prescription
- Times like "1-0-1" or "BD/OD/TDS" = Dosage frequency
- Words like "Before Breakfast", "After Lunch" = Timing instructions

CONTEXT ANALYSIS:
- If symptoms like joint pain, arthritis → Look for: Nucoxia, pain killers, calcium
- If stomach issues mentioned → Look for: Pan D, Pantocid, Rabitex DSR
- If checkboxes for tests → This is a prescription form, medicines are in numbered rows
- If "Urine C/S" or "CBC" checked → Patient has infection, look for antibiotics

OCR TEXT TO ANALYZE:
===
{prescription_text}
===

YOUR MISSION:
1. READ the entire text carefully
2. IDENTIFY anything that LOOKS LIKE a medicine name (even misspelled)
3. CORRECT the spelling to the actual Indian medicine name
4. DETERMINE the dosage (look for numbers like 40, 500, 650 followed by mg)
5. If you see NUMBERED ROWS (1, 2, 3...), those are DEFINITELY medicines

Return a JSON array of ALL medicines you can identify or reasonably infer:

[
  {{"name": "Corrected Medicine Name", "dosage": "40mg", "form": "tablet", "frequency": "OD", "generic_name": "active ingredient"}}
]

If absolutely NO medicines can be identified, return: []

IMPORTANT: Be GENEROUS in detecting medicines. If something COULD be a medicine, include it!

JSON ONLY:"""


async def extract_medicines_from_text(prescription_text: str) -> Dict[str, Any]:
    """
    Extract medicine names and dosages from prescription text using Groq AI.
    """
    if not prescription_text or len(prescription_text.strip()) < 5:
        return {
            "success": False,
            "error": "Prescription text is too short or empty",
            "medicines": []
        }
    
    # Get API key
    api_key = getattr(settings, 'groq_api_key', None) or getattr(settings, 'gemini_api_key', None)
    
    if not api_key:
        return {
            "success": False,
            "error": "No AI API key configured (GROQ_API_KEY or GEMINI_API_KEY)",
            "medicines": []
        }
    
    try:
        prompt = MEDICINE_EXTRACTION_PROMPT.format(prescription_text=prescription_text)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2048
                }
            )
        
        if response.status_code != 200:
            error_text = response.text
            return {
                "success": False,
                "error": f"Groq API error ({response.status_code}): {error_text}",
                "medicines": []
            }
        
        result = response.json()
        response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if not response_text:
            return {
                "success": False,
                "error": "Empty response from AI",
                "medicines": []
            }
        
        # Parse JSON from response
        response_text = response_text.strip()
        
        # Extract JSON array
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            json_str = json_match.group()
        else:
            json_str = response_text
        
        try:
            medicines_data = json.loads(json_str)
        except json.JSONDecodeError:
            json_str = json_str.replace("'", '"')
            json_str = re.sub(r',\s*]', ']', json_str)
            try:
                medicines_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse AI response: {str(e)}",
                    "medicines": [],
                    "raw_response": response_text
                }
        
        # Validate medicines
        medicines = []
        for med_data in medicines_data:
            if isinstance(med_data, dict) and med_data.get("name"):
                name = str(med_data.get("name", "")).strip()
                if name and len(name) > 1:
                    medicine = ExtractedMedicine(
                        name=name,
                        form=str(med_data.get("form", "")).strip(),
                        dosage=str(med_data.get("dosage", "")).strip(),
                        frequency=str(med_data.get("frequency", "")).strip(),
                        quantity=int(med_data.get("quantity", 0)) if med_data.get("quantity") else 0,
                        duration=str(med_data.get("duration", "")).strip(),
                        generic_name=str(med_data.get("generic_name", "")).strip(),
                        is_generic=bool(med_data.get("is_generic", False))
                    )
                    medicines.append(medicine.model_dump())
        
        return {
            "success": True,
            "medicines": medicines,
            "count": len(medicines),
            "raw_response": response_text
        }
        
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "AI request timed out. Please try again.",
            "medicines": []
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"AI extraction failed: {str(e)}",
            "medicines": []
        }


async def find_generic_alternatives(medicine_name: str) -> Dict[str, Any]:
    """Find generic alternatives for a branded medicine."""
    api_key = getattr(settings, 'groq_api_key', None) or getattr(settings, 'gemini_api_key', None)
    
    if not api_key:
        return {"success": False, "error": "No API key", "alternatives": []}
    
    try:
        prompt = f"""For the Indian medicine "{medicine_name}", provide accurate generic alternatives.

Return ONLY a JSON object:
{{"original_name": "{medicine_name}", "generic_name": "salt/composition", "alternatives": [{{"name": "Alternative1", "manufacturer": "Company"}}]}}

JSON ONLY:"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 1024
                }
            )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "success": True,
                    "original_name": data.get("original_name", medicine_name),
                    "generic_name": data.get("generic_name", ""),
                    "alternatives": data.get("alternatives", [])
                }
        
        return {"success": False, "error": "Could not parse", "alternatives": []}
        
    except Exception as e:
        return {"success": False, "error": str(e), "alternatives": []}


async def validate_prescription_text(text: str) -> Dict[str, Any]:
    """Validate if text appears to be from a medical prescription."""
    medical_keywords = [
        "tablet", "capsule", "syrup", "mg", "ml", "dose", "daily",
        "bd", "tds", "od", "sos", "tab", "cap", "inj",
        "nucoxia", "rabitex", "dolo", "pan", "jointset"
    ]
    
    text_lower = text.lower()
    matches = sum(1 for kw in medical_keywords if kw in text_lower)
    confidence = min(matches / 5, 1.0)
    
    return {
        "is_valid": matches >= 2,
        "confidence": round(confidence, 2),
        "keyword_matches": matches
    }
