"""
Gemini Vision-based extractor for valuation reports.
Uses Google's Gemini Pro Vision to extract structured data from PDF images.
"""

import os
import json
import re
import io
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

from .pdf_processor import pdf_to_images


# Extraction prompt template
EXTRACTION_PROMPT = '''You are an expert data extractor for UK Buy to Let Mortgage Valuation Reports.

Analyze this valuation report image and extract ALL visible data into a JSON object.

CRITICAL RULES:
1. For CHECKBOXES: Return true if marked with [X] or ✓, false if empty box, null if not visible
2. For YES/NO fields: Return true for "Yes", false for "No", null if not visible
3. For NUMBERS: Extract numeric value only (remove £, %, m² symbols)
4. For DATES: Convert DD/MM/YYYY to YYYY-MM-DD format
5. For TEXT: Extract exact text as written
6. If a field is not visible or not applicable, use null

Extract data into this EXACT JSON structure (only include fields you can see):

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
    "isBuiltOrOwnedByLocalAuthority": "boolean or null",
    "ownerOccupationPercentage": "number or null",
    "isFlatMaisonetteConverted": "boolean or null",
    "conversionYear": "number or null",
    "isPurposeBuilt": "boolean or null",
    "numberOfUnitsInBlock": "number or null",
    "isAboveCommercial": "boolean or null",
    "residentialNatureImpact": "string or null",
    "tenure": "string or null",
    "isFlyingFreehold": "boolean or null",
    "flyingFreeholdPercentage": "number or null",
    "maintenanceCharge": "number or null",
    "roadCharges": "number or null",
    "groundRent": "number or null",
    "remainingLeaseTermYears": "number or null",
    "isPartCommercialUse": "boolean or null",
    "commercialUsePercentage": "number or null",
    "isPurchasedUnderSharedOwnership": "boolean or null",
    "yearBuilt": "number or null"
  },
  
  "accommodation": {
    "hall": "number or null",
    "livingRooms": "number or null",
    "kitchen": "number or null",
    "isLiftPresent": "boolean or null",
    "utility": "number or null",
    "bedrooms": "number or null",
    "bathrooms": "number or null",
    "separateWc": "number or null",
    "basement": "number or null",
    "garage": "number or null",
    "parking": "number or null",
    "gardens": "boolean or null",
    "isPrivate": "boolean or null",
    "isCommunal": "boolean or null",
    "numberOfOutbuildings": "number or null",
    "outbuildingDetails": "string or null",
    "grossFloorAreaOfDwelling": "number or null"
  },
  
  "currentOccupency": {
    "isEverOccupied": "boolean or null",
    "numberOfAdultsInProperty": "number or null",
    "isHmoOrMultiUnitFreeholdBlock": "boolean or null",
    "isCurrentlyTenanted": "boolean or null",
    "hmoOrMultiUnitDetails": "string or null"
  },
  
  "newBuild": {
    "isNewBuildOrRecentlyConverted": "boolean or null",
    "isCompleted": "boolean or null",
    "isUnderConstruction": "boolean or null",
    "isFinalInspectionRequired": "boolean or null",
    "isNhbcCert": "boolean or null",
    "isBuildZone": "boolean or null",
    "isPremier": "boolean or null",
    "isProfessionalConsultant": "boolean or null",
    "isOtherCert": "boolean or null",
    "otherCertDetails": "string or null",
    "isSelfBuildProject": "boolean or null",
    "isInvolvesPartExchange": "boolean or null",
    "isDisclosureOfIncentivesSeen": "boolean or null",
    "incentivesDetails": "string or null",
    "newBuildDeveloperName": "string or null"
  },
  
  "construction": {
    "isStandardConstruction": "boolean or null",
    "nonStandardConstructionType": "string or null",
    "mainWalls": "string or null",
    "mainRoof": "string or null",
    "garageConstruction": "string or null",
    "outbuildingsConstruction": "string or null",
    "isHasAlterationsOrExtensions": "boolean or null",
    "isAlterationsRequireConsents": "boolean or null",
    "alterationsAge": "number or null"
  },
  
  "localityAndDemand": {
    "isUrban": "boolean or null",
    "isSuburban": "boolean or null",
    "isRural": "boolean or null",
    "isGoodMarketAppeal": "boolean or null",
    "isAverageMarketAppeal": "boolean or null",
    "isPoorMarketAppeal": "boolean or null",
    "isOwnerResidential": "boolean or null",
    "isResidentialLet": "boolean or null",
    "isCommercial": "boolean or null",
    "isPricesRising": "boolean or null",
    "isPricesStatic": "boolean or null",
    "isPricesFalling": "boolean or null",
    "isDemandRising": "boolean or null",
    "isDemandStatic": "boolean or null",
    "isDemandFalling": "boolean or null",
    "isAffectedByCompulsoryPurchase": "boolean or null",
    "compulsoryPurchaseDetails": "string or null",
    "isVacantOrBoardedPropertiesNearby": "boolean or null",
    "vacantOrBoardedDetails": "string or null",
    "isOccupancyRestrictionPossible": "boolean or null",
    "occupancyRestrictionDetails": "string or null",
    "isCloseToHighVoltageEquipment": "boolean or null",
    "highVoltageEquipmentDetails": "string or null"
  },
  
  "services": {
    "isMainsWater": "boolean or null",
    "isPrivateWater": "boolean or null",
    "isUnknownWater": "boolean or null",
    "isGasSupply": "boolean or null",
    "isElectricitySupply": "boolean or null",
    "isCentralHeating": "boolean or null",
    "centralHeatingType": "string or null",
    "isMainDrainage": "boolean or null",
    "isSepticTankPlant": "boolean or null",
    "isUnknownDrainage": "boolean or null",
    "isSolarPanels": "boolean or null",
    "isSharedAccess": "boolean or null",
    "isRoadAdopted": "boolean or null",
    "isHasEasementsOrRightsOfWay": "boolean or null",
    "easementsOrRightsDetails": "string or null",
    "servicesSeparateForFlats": "string or null",
    "servicesSeparateDetails": "string or null"
  },
  
  "conditionsOfProperty": {
    "isStructuralMovement": "boolean or null",
    "isStructuralMovementHistoricOrNonProgressive": "boolean or null",
    "structuralMovementDetails": "string or null",
    "isStructuralModifications": "boolean or null",
    "structuralModificationsDetails": "string or null",
    "communalAreasMaintained": "boolean or null",
    "propertyProneTo": {
      "flooding": "boolean or null",
      "subsidence": "boolean or null",
      "heave": "boolean or null",
      "landslip": "boolean or null",
      "details": "string or null"
    },
    "isPlotBoundariesDefinedUnderPointFourHectares": "boolean or null",
    "isTreesWithinInfluencingDistance": "boolean or null",
    "treesInfluenceDetails": "string or null",
    "isBuiltOnSteepSlope": "boolean or null",
    "steepSlopeDetails": "string or null"
  },
  
  "reports": {
    "isTimberDamp": "boolean or null",
    "isMining": "boolean or null",
    "isElectrical": "boolean or null",
    "isDrains": "boolean or null",
    "isStructuralEngineers": "boolean or null",
    "isArboricultural": "boolean or null",
    "isMundic": "boolean or null",
    "isWallTies": "boolean or null",
    "isRoof": "boolean or null",
    "isMetalliferous": "boolean or null",
    "isSulfateRedAsh": "boolean or null",
    "isOtherReport": "boolean or null",
    "otherReportDetails": "string or null"
  },
  
  "energyEfficiency": {
    "epcRating": "string or null",
    "epcScore": "number or null"
  },
  
  "essentialRepairs": {
    "isEssentialRepairsRequired": "boolean or null",
    "essentialRepairsDetails": "string or null",
    "isReinspectionRequired": "boolean or null"
  },
  
  "rentalInformation": {
    "isRentalDemandInLocality": "boolean or null",
    "rentalDemandDetails": "string or null",
    "monthlyMarketRentPresentCondition": "number or null",
    "monthlyMarketRentImprovedCondition": "number or null",
    "isOtherLettingDemandFactors": "boolean or null",
    "otherLettingDemandDetails": "string or null",
    "investorOnlyDemand": "boolean or null",
    "investorOnlyDemandDetails": "string or null"
  },
  
  "valuationForFinancePurpose": {
    "valuationComparativeOnly": "string or null",
    "isSuitableForFinance": "boolean or null",
    "financeSuitabilityDetails": "string or null",
    "marketValuePresentCondition": "number or null",
    "marketValueAfterRepairs": "number or null",
    "purchasePriceOrBorrowerEstimate": "number or null",
    "buildingInsuranceReinstatementCost": "number or null",
    "isInsurancePremiumLoadingRisk": "boolean or null",
    "insurancePremiumLoadingDetails": "string or null"
  },
  
  "generalRemarks": "string or null",
  
  "valuersDeclaration": {
    "valuerSignature": "string or null",
    "valuerName": "string or null",
    "onBehalfOf": "string or null",
    "telephone": "string or null",
    "fax": "string or null",
    "email": "string or null",
    "valuerQualifications": {
      "mrics": "boolean or null",
      "frics": "boolean or null",
      "assocRics": "boolean or null"
    },
    "ricsNumber": "number or null",
    "valuerAddress": "string or null",
    "valuerPostcode": "string or null",
    "reportDate": "YYYY-MM-DD or null"
  }
}

IMPORTANT: Return ONLY valid JSON. No markdown, no explanations. Just the JSON object.
Extract only what you can clearly see in this page. For unseen fields, use null.
'''


def get_client(api_key: Optional[str] = None) -> genai.Client:
    """Get configured Gemini client"""
    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError(
            "Google API key not found. Set GOOGLE_API_KEY environment variable "
            "or pass api_key parameter."
        )
    return genai.Client(api_key=key)


def extract_json_from_response(text: str) -> Dict[str, Any]:
    """
    Extract JSON from Gemini response, handling markdown code blocks.
    """
    # Try to find JSON in code blocks first
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if json_match:
        text = json_match.group(1)
    
    # Clean up the text
    text = text.strip()
    
    # Try to parse as JSON
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
        raise ValueError(f"Could not parse JSON from response: {e}\nResponse: {text[:500]}...")


def merge_page_extractions(extractions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge extractions from multiple pages into a single document.
    Later pages override earlier pages for non-null values.
    """
    merged = {}
    
    for extraction in extractions:
        for key, value in extraction.items():
            if value is None:
                continue
            
            if isinstance(value, dict):
                # Merge nested objects
                if key not in merged:
                    merged[key] = {}
                if isinstance(merged.get(key), dict):
                    merged[key] = merge_page_extractions([merged[key], value])
                else:
                    merged[key] = value
            else:
                # Simple value - use the first non-null value found
                if key not in merged or merged[key] is None:
                    merged[key] = value
    
    return merged


def pil_image_to_bytes(image: Image.Image) -> bytes:
    """Convert PIL Image to bytes for API"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.read()


def extract_from_image_with_retry(
    client: genai.Client,
    image: Image.Image,
    model_name: str = "gemini-2.0-flash",
    max_retries: int = 3,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Extract data from a single image using Gemini Vision with retry logic.
    
    Args:
        client: Gemini client
        image: PIL Image object
        model_name: Gemini model to use
        max_retries: Maximum number of retries for rate limit errors
        verbose: Print progress information
        
    Returns:
        Extracted data as dictionary
    """
    # Convert image to bytes
    image_bytes = pil_image_to_bytes(image)
    
    # Create image part using from_bytes
    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type="image/png"
    )
    
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            # Generate content with image
            response = client.models.generate_content(
                model=model_name,
                contents=[EXTRACTION_PROMPT, image_part],
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Low temperature for consistent extraction
                    max_output_tokens=8192,
                )
            )
            
            # Parse the response
            return extract_json_from_response(response.text)
            
        except Exception as e:
            last_error = e
            error_str = str(e)
            
            # Check if it's a retryable error (429 rate limit or 503 unavailable)
            is_rate_limit = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str
            is_unavailable = "503" in error_str or "UNAVAILABLE" in error_str
            
            if is_rate_limit or is_unavailable:
                # Parse retry delay from error message
                retry_delay = 30 if is_unavailable else 45  # Shorter delay for 503
                retry_match = re.search(r'retry in (\d+)', error_str.lower())
                if retry_match:
                    retry_delay = int(retry_match.group(1)) + 5  # Add buffer
                
                error_type = "Model overloaded (503)" if is_unavailable else "Rate limit (429)"
                
                if attempt < max_retries:
                    if verbose:
                        print(f"    {error_type}. Waiting {retry_delay}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(retry_delay)
                    continue
                else:
                    if verbose:
                        print(f"    {error_type} - exceeded {max_retries} retries")
                    raise
            else:
                # Not a retryable error, raise immediately
                raise
    
    raise last_error


def extract_from_pdf(
    pdf_path: str,
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.0-flash",
    verbose: bool = True,
    max_retries: int = 3,
    delay_between_pages: float = 2.0
) -> Dict[str, Any]:
    """
    Extract valuation report data from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        api_key: Google API key (optional, uses env var if not provided)
        model_name: Gemini model to use
        verbose: Print progress information
        max_retries: Maximum retries per page for rate limits
        delay_between_pages: Seconds to wait between pages
        
    Returns:
        Merged extraction data as dictionary
    """
    # Get client
    client = get_client(api_key)
    
    if verbose:
        print(f"Processing PDF: {pdf_path}")
        print(f"Using model: {model_name}")
    
    # Convert PDF to images
    if verbose:
        print("Converting PDF to images...")
    images = pdf_to_images(pdf_path, dpi=200)
    
    if verbose:
        print(f"Found {len(images)} pages")
    
    # Extract from each page (skip photo pages - usually last 2)
    extractions = []
    pages_to_process = min(len(images), 5)  # Usually only first 4-5 pages have data
    
    for i, image in enumerate(images[:pages_to_process], start=1):
        if verbose:
            print(f"Extracting page {i}/{pages_to_process}...")
        
        try:
            extraction = extract_from_image_with_retry(
                client, image, model_name, 
                max_retries=max_retries,
                verbose=verbose
            )
            extractions.append(extraction)
            
            if verbose:
                # Count non-null fields
                def count_fields(obj, prefix=""):
                    count = 0
                    for k, v in obj.items() if isinstance(obj, dict) else []:
                        if isinstance(v, dict):
                            count += count_fields(v, f"{prefix}{k}.")
                        elif v is not None:
                            count += 1
                    return count
                field_count = count_fields(extraction)
                print(f"  ✓ Extracted {field_count} fields")
            
            # Delay between pages to avoid rate limits
            if i < pages_to_process and delay_between_pages > 0:
                time.sleep(delay_between_pages)
                
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
    # Test the extractor
    import sys
    from dotenv import load_dotenv
    
    load_dotenv()
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        result = extract_from_pdf(pdf_path, verbose=True)
        print("\n--- Extracted Data ---")
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python vision_extractor.py <path_to_pdf>")
