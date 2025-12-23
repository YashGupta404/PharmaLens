"""
OCR Service

Google Cloud Vision API integration for text extraction from prescription images.
"""

from google.cloud import vision
from google.oauth2 import service_account
from typing import Tuple, Optional, List, Dict, Any
import httpx
import os

from app.config import settings


def get_vision_client() -> vision.ImageAnnotatorClient:
    """
    Get Google Cloud Vision client.
    Uses credentials from GOOGLE_APPLICATION_CREDENTIALS environment variable.
    """
    credentials_path = settings.google_application_credentials
    
    if not credentials_path:
        raise ValueError(
            "GOOGLE_APPLICATION_CREDENTIALS not configured in .env"
        )
    
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            f"Google credentials file not found: {credentials_path}"
        )
    
    # Set environment variable for Google SDK
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    
    return vision.ImageAnnotatorClient()


async def extract_text_from_url(image_url: str) -> Dict[str, Any]:
    """
    Extract text from an image URL using Google Cloud Vision.
    
    Args:
        image_url: URL of the image (Cloudinary URL)
    
    Returns:
        Dict with:
        - success: bool
        - text: extracted text
        - confidence: average confidence score
        - blocks: list of text blocks with positions
    """
    try:
        client = get_vision_client()
        
        # Create image from URL
        image = vision.Image()
        image.source.image_uri = image_url
        
        # Perform text detection (supports both printed and handwritten)
        response = client.document_text_detection(image=image)
        
        if response.error.message:
            return {
                "success": False,
                "error": response.error.message,
                "text": "",
                "confidence": 0.0
            }
        
        # Get full text
        full_text = response.full_text_annotation.text if response.full_text_annotation else ""
        
        # Calculate average confidence
        confidences = []
        blocks = []
        
        if response.full_text_annotation:
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    block_text = ""
                    block_confidence = block.confidence if hasattr(block, 'confidence') else 0
                    
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            word_text = "".join([symbol.text for symbol in word.symbols])
                            block_text += word_text + " "
                            if hasattr(word, 'confidence'):
                                confidences.append(word.confidence)
                    
                    blocks.append({
                        "text": block_text.strip(),
                        "confidence": block_confidence,
                        "type": str(block.block_type)
                    })
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "success": True,
            "text": full_text.strip(),
            "confidence": round(avg_confidence, 4),
            "blocks": blocks,
            "word_count": len(full_text.split()) if full_text else 0
        }
        
    except FileNotFoundError as e:
        return {
            "success": False,
            "error": str(e),
            "text": "",
            "confidence": 0.0
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"OCR failed: {str(e)}",
            "text": "",
            "confidence": 0.0
        }


async def extract_text_from_bytes(image_bytes: bytes) -> Dict[str, Any]:
    """
    Extract text from image bytes.
    
    Args:
        image_bytes: Raw image bytes
    
    Returns:
        Dict with extracted text and metadata
    """
    try:
        client = get_vision_client()
        
        # Create image from bytes
        image = vision.Image(content=image_bytes)
        
        # Perform document text detection (better for prescriptions)
        response = client.document_text_detection(image=image)
        
        if response.error.message:
            return {
                "success": False,
                "error": response.error.message,
                "text": "",
                "confidence": 0.0
            }
        
        full_text = response.full_text_annotation.text if response.full_text_annotation else ""
        
        # Calculate confidence
        confidences = []
        if response.full_text_annotation:
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            if hasattr(word, 'confidence'):
                                confidences.append(word.confidence)
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "success": True,
            "text": full_text.strip(),
            "confidence": round(avg_confidence, 4),
            "word_count": len(full_text.split()) if full_text else 0
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"OCR failed: {str(e)}",
            "text": "",
            "confidence": 0.0
        }


async def detect_labels(image_url: str) -> List[str]:
    """
    Detect labels/objects in an image.
    Useful for verifying if the image is a prescription.
    
    Args:
        image_url: URL of the image
    
    Returns:
        List of detected labels
    """
    try:
        client = get_vision_client()
        
        image = vision.Image()
        image.source.image_uri = image_url
        
        response = client.label_detection(image=image)
        
        labels = [label.description for label in response.label_annotations]
        return labels
        
    except Exception:
        return []


def is_prescription_image(labels: List[str]) -> bool:
    """
    Check if the image appears to be a prescription based on labels.
    
    Args:
        labels: List of detected labels
    
    Returns:
        True if likely a prescription
    """
    prescription_keywords = [
        "document", "paper", "text", "handwriting", "receipt",
        "prescription", "medical", "medicine", "pharmacy",
        "font", "writing", "letter", "number"
    ]
    
    labels_lower = [label.lower() for label in labels]
    
    matches = sum(1 for kw in prescription_keywords if any(kw in label for label in labels_lower))
    
    return matches >= 2
