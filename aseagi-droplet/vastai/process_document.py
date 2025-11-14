"""
Document Processing Module for Vast.ai Worker
GPU-accelerated OCR and Claude Vision analysis
"""

import os
import sys
import base64
from pathlib import Path
from typing import Dict, Optional
import logging

from PIL import Image
import anthropic

# Configure logging
logger = logging.getLogger(__name__)

# Tesseract (optional)
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("Tesseract not available - using Claude Vision only")

# Anthropic client
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    logger.error("ANTHROPIC_API_KEY not set")
    sys.exit(1)

claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def extract_text_tesseract(image_path: str) -> Optional[str]:
    """Extract text using Tesseract OCR (Tier 1 - Fast & Free)"""
    if not TESSERACT_AVAILABLE:
        return None

    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip() if text else None
    except Exception as e:
        logger.error(f"Tesseract OCR failed: {e}")
        return None


def extract_text_claude(image_path: str) -> Dict:
    """Extract text using Claude Vision (Tier 2 - Accurate & Smart)"""
    try:
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')

        # Detect image type
        ext = Path(image_path).suffix.lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_type_map.get(ext, 'image/jpeg')

        # Claude Vision prompt
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": """Analyze this document and extract all information.

Return a JSON response with:
{
    "text": "Full extracted text from the document",
    "document_type": "Type of document (legal, financial, personal, medical, business, receipt, etc.)",
    "category": "Specific category (contract, invoice, tax form, court document, etc.)",
    "key_entities": ["List", "of", "key", "people/organizations/dates"],
    "summary": "Brief 2-3 sentence summary",
    "relevancy_score": 0-1000,
    "macro_score": 0-1000,
    "micro_score": 0-1000,
    "legal_score": 0-1000,
    "category_score": 0-1000,
    "document_date": "YYYY-MM-DD if found, null otherwise"
}

Scoring guidelines:
- relevancy_score: Overall importance (0=junk mail, 1000=critical legal doc)
- macro_score: High-level significance (strategic/life impact)
- micro_score: Detail quality (completeness, readability)
- legal_score: Legal importance (0=none, 1000=court order/contract)
- category_score: Category-specific value

Return ONLY the JSON, no other text."""
                    }
                ]
            }]
        )

        # Parse response
        response_text = response.content[0].text

        # Try to extract JSON from response
        import json

        # Sometimes Claude wraps JSON in markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        result = json.loads(response_text)

        # Add cost tracking (Claude 3.5 Sonnet pricing)
        # Input: $3/MTok, Output: $15/MTok
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = (input_tokens / 1_000_000 * 3.0) + (output_tokens / 1_000_000 * 15.0)
        result['api_cost'] = cost

        logger.info(f"Claude Vision extracted: {len(result.get('text', ''))} chars, cost: ${cost:.4f}")

        return result

    except Exception as e:
        logger.error(f"Claude Vision failed: {e}")
        return {
            "text": "",
            "document_type": "error",
            "category": "processing_error",
            "error": str(e),
            "api_cost": 0.0
        }


def process_document(file_path: str) -> Dict:
    """
    Main processing function - Tiered OCR approach
    1. Try Tesseract (fast, free)
    2. Fall back to Claude Vision (accurate, paid)
    """
    logger.info(f"Processing: {file_path}")

    result = {
        "file_path": file_path,
        "file_name": Path(file_path).name,
        "text": "",
        "document_type": "unknown",
        "category": "unknown",
        "relevancy_number": 0,
        "macro_score": 0,
        "micro_score": 0,
        "legal_score": 0,
        "category_score": 0,
        "api_cost": 0.0,
        "ocr_method": "none"
    }

    # Check file type
    ext = Path(file_path).suffix.lower()
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']

    if ext not in image_extensions:
        logger.warning(f"Unsupported file type: {ext}")
        result['error'] = f"Unsupported file type: {ext}"
        return result

    # Tier 1: Try Tesseract first (if available)
    if TESSERACT_AVAILABLE:
        tesseract_text = extract_text_tesseract(file_path)

        if tesseract_text and len(tesseract_text) > 50:
            # Tesseract succeeded with decent text
            logger.info(f"✅ Tesseract extracted {len(tesseract_text)} chars")
            result['text'] = tesseract_text
            result['ocr_method'] = 'tesseract'

            # Still use Claude for categorization only (cheaper)
            # But skip if we want pure Tesseract
            # For now, we'll use Tesseract text as-is
            # TODO: Add lightweight categorization

            return result

    # Tier 2: Claude Vision (fallback or primary)
    logger.info("Using Claude Vision for extraction")
    claude_result = extract_text_claude(file_path)

    if claude_result and not claude_result.get('error'):
        result.update({
            'text': claude_result.get('text', ''),
            'document_type': claude_result.get('document_type', 'unknown'),
            'category': claude_result.get('category', 'unknown'),
            'relevancy_number': claude_result.get('relevancy_score', 0),
            'macro_score': claude_result.get('macro_score', 0),
            'micro_score': claude_result.get('micro_score', 0),
            'legal_score': claude_result.get('legal_score', 0),
            'category_score': claude_result.get('category_score', 0),
            'document_date': claude_result.get('document_date'),
            'summary': claude_result.get('summary', ''),
            'key_entities': claude_result.get('key_entities', []),
            'api_cost': claude_result.get('api_cost', 0.0),
            'ocr_method': 'claude_vision'
        })

        logger.info(f"✅ Claude Vision extracted {len(result['text'])} chars, "
                   f"relevancy: {result['relevancy_number']}, cost: ${result['api_cost']:.4f}")
    else:
        logger.error("Both OCR methods failed")
        result['error'] = claude_result.get('error', 'OCR failed')

    return result


if __name__ == "__main__":
    # Test processing
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        result = process_document(test_file)
        import json
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python process_document.py <image_file>")
