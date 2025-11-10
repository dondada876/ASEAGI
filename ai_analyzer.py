"""
AI Document Analyzer for ASEAGI Legal Documents
Adapted from don1_automation with legal-specific enhancements

Supports:
- Anthropic Claude 3.5 Sonnet (recommended)
- OpenAI GPT-4 Vision (alternative)

Extracts:
- Document type (legal-specific)
- Date (YYYY-MM-DD)
- Title
- Relevancy score (0-1000, PROJ344 compatible)
- Summary (2-3 sentences with legal context)
- Confidence scores per field
"""

import os
import base64
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

# Legal document types for ASEAGI
LEGAL_DOC_TYPES = {
    "police_report": "PLCR",
    "declaration": "DECL",
    "evidence": "EVID",
    "cps_report": "CPSR",
    "response": "RESP",
    "forensic_report": "FORN",
    "court_order": "ORDR",
    "motion": "MOTN",
    "hearing_transcript": "HEAR",
    "other": "OTHR"
}

class DocumentAnalyzer:
    """AI-powered document analysis using Claude or GPT-4 Vision"""

    def __init__(self, provider: str = "anthropic", confidence_threshold: int = 70):
        """
        Initialize the analyzer

        Args:
            provider: "anthropic" or "openai"
            confidence_threshold: Minimum confidence (0-100) before asking questions
        """
        self.provider = provider.lower()
        self.confidence_threshold = confidence_threshold

        if self.provider == "anthropic":
            try:
                from anthropic import Anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY not set")
                self.client = Anthropic(api_key=api_key)
                self.model = "claude-3-5-sonnet-20241022"
            except ImportError:
                raise ImportError("Install: pip install anthropic")

        elif self.provider == "openai":
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not set")
                self.client = OpenAI(api_key=api_key)
                self.model = "gpt-4-vision-preview"
            except ImportError:
                raise ImportError("Install: pip install openai")
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'anthropic' or 'openai'")

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _get_analysis_prompt(self) -> str:
        """Get the legal-specific analysis prompt"""
        return """You are a legal document analysis AI assistant for a child custody case.

Analyze this document image and extract the following information with high accuracy:

1. **Document Type**: Classify as ONE of these legal document types:
   - police_report: Official police reports, incident reports, police body cam transcripts
   - declaration: Legal declarations, affidavits, sworn statements
   - evidence: Photos, screenshots, physical evidence, forensic photos
   - cps_report: Child Protective Services reports, social worker reports, dependency reports
   - response: Legal responses, replies to motions, oppositions
   - forensic_report: Medical evaluations, psychological evaluations, SART exams
   - court_order: Court orders, judgments, rulings, minute orders
   - motion: Legal motions, petitions, requests for orders
   - hearing_transcript: Court hearing transcripts, depositions, testimony
   - other: Any other legal document type

2. **Date**: Document date in YYYY-MM-DD format (look for date created, filed, or signed)

3. **Title**: Brief descriptive title (max 100 characters). Focus on what makes this document significant.

4. **Relevancy Score (0-1000)** - PROJ344 Legal Scoring:
   - 900-1000: SMOKING GUN - Critical evidence (perjury, smoking gun, constitutional violations, child safety threats)
   - 800-899: HIGH - Strong evidence (contradicts opposition claims, proves case facts, expert testimony)
   - 700-799: IMPORTANT - Supporting evidence (corroborating evidence, background context, procedural documents)
   - 600-699: USEFUL - Background information (general context, administrative documents)
   - 0-599: REFERENCE - Minimal legal relevance

5. **Summary**: Write 2-3 sentences highlighting:
   - What this document is
   - Why it's legally significant
   - How it relates to child custody/safety issues
   - Any smoking gun evidence, perjury, or violations detected

6. **Legal Indicators**: Identify if present:
   - smoking_gun: Evidence that strongly proves case
   - perjury_indicator: False statements under oath
   - fraud_indicator: Deceptive practices
   - constitutional_violation: Due process, rights violations
   - child_safety_concern: Immediate safety issues

Return your analysis as a JSON object with this exact structure:
{
  "document_type": "police_report",
  "date": "2024-11-06",
  "title": "Berkeley PD Report - Child Was Safe with Mother",
  "relevancy": 920,
  "summary": "Police report from November 6, 2024 documenting that child was found safe and happy with mother. Officer noted no signs of distress or danger. This contradicts CPS claims that mother was unfit.",
  "legal_indicators": {
    "smoking_gun": true,
    "perjury_indicator": false,
    "fraud_indicator": true,
    "constitutional_violation": false,
    "child_safety_concern": false
  },
  "confidence_scores": {
    "type": 95,
    "date": 90,
    "title": 85,
    "relevancy": 80,
    "summary": 85
  },
  "overall_confidence": 87,
  "needs_clarification": false,
  "questions": []
}

**Confidence Scoring Instructions:**
- Return confidence (0-100%) for each extracted field
- Be honest about uncertainty
- If confidence for any field is below 70%, set needs_clarification=true
- Add specific questions to the "questions" array for fields with low confidence
- overall_confidence should be the average of all field confidences

**Important:**
- Be conservative with relevancy scores - only use 900+ for truly critical evidence
- Focus on legal significance, not just emotional impact
- Identify perjury/fraud/violations explicitly
- If text is unclear, lower confidence and ask questions
"""

    def analyze_document(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze a legal document image

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary with extracted metadata and confidence scores
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Encode image
        image_base64 = self._encode_image(image_path)

        # Get prompt
        prompt = self._get_analysis_prompt()

        # Call AI provider
        if self.provider == "anthropic":
            result = self._analyze_with_claude(image_base64, prompt)
        else:
            result = self._analyze_with_openai(image_base64, prompt)

        # Map document type to ASEAGI code
        if result.get("document_type") in LEGAL_DOC_TYPES:
            result["document_type_code"] = LEGAL_DOC_TYPES[result["document_type"]]
        else:
            result["document_type_code"] = "OTHR"

        # Check if clarification needed
        if result["overall_confidence"] < self.confidence_threshold:
            result["needs_clarification"] = True

        return result

    def _analyze_with_claude(self, image_base64: str, prompt: str) -> Dict[str, Any]:
        """Analyze with Anthropic Claude"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )

            # Extract JSON from response
            content = response.content[0].text

            # Try to parse JSON
            # Look for JSON block in markdown code fence or raw JSON
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                # Try to find JSON object
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                json_str = content[json_start:json_end]

            result = json.loads(json_str)
            return result

        except Exception as e:
            # Return error result with 0 confidence
            return {
                "document_type": "other",
                "document_type_code": "OTHR",
                "date": None,
                "title": "Error analyzing document",
                "relevancy": 0,
                "summary": f"AI analysis failed: {str(e)}",
                "legal_indicators": {},
                "confidence_scores": {
                    "type": 0,
                    "date": 0,
                    "title": 0,
                    "relevancy": 0,
                    "summary": 0
                },
                "overall_confidence": 0,
                "needs_clarification": True,
                "questions": ["AI analysis failed. Please enter metadata manually."],
                "error": str(e)
            }

    def _analyze_with_openai(self, image_base64: str, prompt: str) -> Dict[str, Any]:
        """Analyze with OpenAI GPT-4 Vision"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )

            content = response.choices[0].message.content

            # Parse JSON from response (same logic as Claude)
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                json_str = content[json_start:json_end]

            result = json.loads(json_str)
            return result

        except Exception as e:
            return {
                "document_type": "other",
                "document_type_code": "OTHR",
                "date": None,
                "title": "Error analyzing document",
                "relevancy": 0,
                "summary": f"AI analysis failed: {str(e)}",
                "legal_indicators": {},
                "confidence_scores": {
                    "type": 0,
                    "date": 0,
                    "title": 0,
                    "relevancy": 0,
                    "summary": 0
                },
                "overall_confidence": 0,
                "needs_clarification": True,
                "questions": ["AI analysis failed. Please enter metadata manually."],
                "error": str(e)
            }


def test_analyzer():
    """Test the document analyzer"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ai_analyzer.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    # Try Anthropic first, fall back to OpenAI
    provider = "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "openai"

    print(f"Using provider: {provider}")
    print(f"Analyzing: {image_path}\n")

    analyzer = DocumentAnalyzer(provider=provider)
    result = analyzer.analyze_document(image_path)

    print(json.dumps(result, indent=2))

    # Summary
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    print(f"Type: {result['document_type']} ({result.get('document_type_code', 'N/A')})")
    print(f"Date: {result.get('date', 'Unknown')}")
    print(f"Title: {result.get('title', 'N/A')}")
    print(f"Relevancy: {result.get('relevancy', 0)}/1000")
    print(f"Confidence: {result.get('overall_confidence', 0)}%")
    print(f"Needs Clarification: {result.get('needs_clarification', True)}")

    if result.get('questions'):
        print("\nQuestions:")
        for q in result['questions']:
            print(f"  - {q}")


if __name__ == "__main__":
    test_analyzer()
