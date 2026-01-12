"""
JSON storage module for extracted valuation reports.
Saves extraction results to JSON files.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


def save_extraction(
    data: Dict[str, Any],
    output_dir: str = "output",
    filename: Optional[str] = None,
    source_pdf: Optional[str] = None
) -> str:
    """
    Save extracted data to a JSON file.
    
    Args:
        data: Extracted data dictionary
        output_dir: Directory to save output files
        filename: Output filename (without extension). If None, generates from source_pdf
        source_pdf: Original PDF path (used for filename and metadata)
        
    Returns:
        Path to the saved JSON file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename if not provided
    if filename is None:
        if source_pdf:
            # Use PDF filename without extension
            filename = Path(source_pdf).stem
        else:
            # Use timestamp
            filename = f"extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Add metadata
    output_data = {
        "_metadata": {
            "extractedAt": datetime.now().isoformat(),
            "sourcePdf": source_pdf,
            "version": "1.0"
        },
        **data
    }
    
    # Build output path
    output_path = os.path.join(output_dir, f"{filename}.json")
    
    # Save to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    return output_path


def load_extraction(json_path: str) -> Dict[str, Any]:
    """
    Load previously extracted data from a JSON file.
    
    Args:
        json_path: Path to the JSON file
        
    Returns:
        Extracted data dictionary
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == "__main__":
    # Test the module
    test_data = {
        "applicantName": "Test User",
        "applicationNumber": "12345-6789",
        "propertyType": {
            "isFlat": True,
            "flatMaisonetteFloor": 5
        }
    }
    
    output_path = save_extraction(test_data, source_pdf="test.pdf")
    print(f"Saved to: {output_path}")
    
    loaded = load_extraction(output_path)
    print(f"Loaded: {json.dumps(loaded, indent=2)}")
