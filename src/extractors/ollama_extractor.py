"""
Ollama Vision-based extractor for valuation reports.
Uses local Ollama with LLaVA or similar vision models - completely FREE with no API limits.
"""

import os
import json
import re
import io
import base64
import requests
from typing import List, Dict, Any, Optional
from PIL import Image

from .pdf_processor import pdf_to_images


# Extraction prompt template (same as Gemini version)
EXTRACTION_PROMPT = '''You are an expert data extractor for UK Buy to Let Mortgage Valuation Reports.

Analyze this valuation report image and extract ALL visible data into a JSON object.

CRITICAL RULES:
1. For CHECKBOXES: Return true if marked with [X] or ✓, false if empty box, null if not visible
2. For YES/NO fields: Return true for "Yes", false for "No", null if not visible
3. For NUMBERS: Extract numeric value only (remove £, %, m² symbols)
4. For DATES: Convert DD/MM/YYYY to YYYY-MM-DD format
5. For TEXT: Extract exact text as written
6. If a field is not visible or not applicable, use null

Extract data into this JSON structure (only include fields you can see):

{
  "applicationType": "string or null",
  "applicationNumber": "string or null", 
  "applicantName": "string or null",
  "dateOfInspection": "YYYY-MM-DD or null",
  "propertyAddress": "string or null",
  "postCode": "string or null",
  "propertyType": {
    "isDetachedHouse": "boolean or null",
    "isSemiDetachedHouse": "boolean or null",
    "isTerracedHouse": "boolean or null",
    "isBungalow": "boolean or null",
    "isFlat": "boolean or null",
    "isMaisonette": "boolean or null",
    "flatMaisonetteFloor": "number or null",
    "numberOfFloorsInBlock": "number or null",
    "tenure": "Freehold or Leasehold or null",
    "yearBuilt": "number or null"
  },
  "accommodation": {
    "bedrooms": "number or null",
    "bathrooms": "number or null",
    "livingRooms": "number or null",
    "kitchen": "number or null",
    "grossFloorAreaOfDwelling": "number or null"
  },
  "currentOccupency": {
    "isEverOccupied": "boolean or null",
    "isCurrentlyTenanted": "boolean or null"
  },
  "construction": {
    "isStandardConstruction": "boolean or null",
    "mainWalls": "string or null",
    "mainRoof": "string or null"
  },
  "services": {
    "isMainsWater": "boolean or null",
    "isGasSupply": "boolean or null",
    "isElectricitySupply": "boolean or null",
    "isCentralHeating": "boolean or null"
  },
  "energyEfficiency": {
    "epcRating": "string A-G or null",
    "epcScore": "number 1-100 or null"
  },
  "rentalInformation": {
    "monthlyMarketRentPresentCondition": "number or null"
  },
  "valuationForFinancePurpose": {
    "marketValuePresentCondition": "number or null",
    "purchasePriceOrBorrowerEstimate": "number or null"
  },
  "valuersDeclaration": {
    "valuerName": "string or null",
    "reportDate": "YYYY-MM-DD or null"
  }
}

Return ONLY valid JSON. No markdown, no explanations. Just the JSON object.
'''


def check_ollama_available(base_url: str = "http://localhost:11434") -> bool:
    """Check if Ollama is running and accessible"""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def list_ollama_models(base_url: str = "http://localhost:11434") -> List[str]:
    """List available Ollama models"""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
    except:
        pass
    return []


def pil_image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')


def extract_json_from_response(text: str) -> Dict[str, Any]:
    """Extract JSON from response, handling markdown code blocks"""
    # Try to find JSON in code blocks first
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if json_match:
        text = json_match.group(1)
    
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Try to find JSON object boundaries
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Could not parse JSON: {e}\nResponse: {text[:500]}...")


def merge_page_extractions(extractions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge extractions from multiple pages"""
    merged = {}
    
    for extraction in extractions:
        for key, value in extraction.items():
            if value is None:
                continue
            
            if isinstance(value, dict):
                if key not in merged:
                    merged[key] = {}
                if isinstance(merged.get(key), dict):
                    merged[key] = merge_page_extractions([merged[key], value])
                else:
                    merged[key] = value
            else:
                if key not in merged or merged[key] is None:
                    merged[key] = value
    
    return merged


def extract_from_image_ollama(
    image: Image.Image,
    model_name: str = "llava",
    base_url: str = "http://localhost:11434",
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Extract data from a single image using Ollama vision model.
    
    Args:
        image: PIL Image object
        model_name: Ollama model to use (llava, llava:13b, bakllava, etc.)
        base_url: Ollama API base URL
        verbose: Print progress
        
    Returns:
        Extracted data as dictionary
    """
    # Convert image to base64
    image_base64 = pil_image_to_base64(image)
    
    # Call Ollama API
    response = requests.post(
        f"{base_url}/api/generate",
        json={
            "model": model_name,
            "prompt": EXTRACTION_PROMPT,
            "images": [image_base64],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 4096
            }
        },
        timeout=300  # 5 minutes timeout for large images
    )
    
    if response.status_code != 200:
        raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    
    result = response.json()
    response_text = result.get("response", "")
    
    return extract_json_from_response(response_text)


def extract_from_pdf_ollama(
    pdf_path: str,
    model_name: str = "llava",
    base_url: str = "http://localhost:11434",
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Extract valuation report data from a PDF file using Ollama.
    
    Args:
        pdf_path: Path to the PDF file
        model_name: Ollama model to use
        base_url: Ollama API base URL
        verbose: Print progress information
        
    Returns:
        Merged extraction data as dictionary
    """
    if verbose:
        print(f"Processing PDF: {pdf_path}")
        print(f"Using Ollama model: {model_name}")
        print(f"Ollama URL: {base_url}")
    
    # Check Ollama is running
    if not check_ollama_available(base_url):
        raise Exception(
            f"Ollama is not running at {base_url}.\n"
            "Please install and start Ollama:\n"
            "  1. Download from https://ollama.ai\n"
            "  2. Run: ollama serve\n"
            "  3. Pull a vision model: ollama pull llava"
        )
    
    # Check model is available
    available_models = list_ollama_models(base_url)
    if verbose:
        print(f"Available models: {', '.join(available_models) or 'none'}")
    
    if not any(model_name in m for m in available_models):
        raise Exception(
            f"Model '{model_name}' not found.\n"
            f"Available models: {available_models}\n"
            f"Pull the model with: ollama pull {model_name}"
        )
    
    # Convert PDF to images
    if verbose:
        print("Converting PDF to images...")
    images = pdf_to_images(pdf_path, dpi=150)  # Lower DPI for faster processing
    
    if verbose:
        print(f"Found {len(images)} pages")
    
    # Extract from each page
    extractions = []
    pages_to_process = min(len(images), 4)  # Process first 4 pages
    
    for i, image in enumerate(images[:pages_to_process], start=1):
        if verbose:
            print(f"Extracting page {i}/{pages_to_process}...")
        
        try:
            extraction = extract_from_image_ollama(
                image, model_name, base_url, verbose
            )
            extractions.append(extraction)
            
            if verbose:
                def count_fields(obj):
                    count = 0
                    for k, v in obj.items() if isinstance(obj, dict) else []:
                        if isinstance(v, dict):
                            count += count_fields(v)
                        elif v is not None:
                            count += 1
                    return count
                field_count = count_fields(extraction)
                print(f"  ✓ Extracted {field_count} fields")
                
        except Exception as e:
            if verbose:
                print(f"  ✗ Error on page {i}: {e}")
            continue
    
    # Merge all page extractions
    if verbose:
        print("Merging page extractions...")
    
    merged = merge_page_extractions(extractions)
    
    if verbose:
        def count_fields(obj):
            count = 0
            for k, v in obj.items() if isinstance(obj, dict) else []:
                if isinstance(v, dict):
                    count += count_fields(v)
                elif v is not None:
                    count += 1
            return count
        total_fields = count_fields(merged)
        print(f"Total extracted fields: {total_fields}")
    
    return merged


if __name__ == "__main__":
    import sys
    
    print("Checking Ollama availability...")
    
    if check_ollama_available():
        print("✓ Ollama is running")
        models = list_ollama_models()
        print(f"Available models: {models}")
    else:
        print("✗ Ollama is not running")
        print("\nTo use Ollama (FREE, local, unlimited):")
        print("  1. Download from https://ollama.ai")
        print("  2. Run: ollama serve")
        print("  3. Pull a vision model: ollama pull llava")
        sys.exit(1)
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        result = extract_from_pdf_ollama(pdf_path, verbose=True)
        print("\n--- Extracted Data ---")
        print(json.dumps(result, indent=2))
