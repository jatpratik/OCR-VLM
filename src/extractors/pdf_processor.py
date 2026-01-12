"""
PDF to Image processor using pdf2image.
Converts PDF pages to high-resolution images for vision LLM processing.
"""

import os
import base64
from io import BytesIO
from pathlib import Path
from typing import List, Tuple
from PIL import Image

# Try to import pdf2image, provide helpful error if not available
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


def check_poppler_installed() -> bool:
    """Check if Poppler is installed and accessible"""
    if not PDF2IMAGE_AVAILABLE:
        return False
    try:
        # Try a minimal conversion to test
        return True
    except Exception:
        return False


def pdf_to_images(pdf_path: str, dpi: int = 200) -> List[Image.Image]:
    """
    Convert PDF pages to PIL Images.
    
    Args:
        pdf_path: Path to the PDF file
        dpi: Resolution for conversion (higher = better quality but slower)
        
    Returns:
        List of PIL Image objects, one per page
    """
    if not PDF2IMAGE_AVAILABLE:
        raise ImportError(
            "pdf2image is not installed. Install it with: pip install pdf2image\n"
            "Also ensure Poppler is installed:\n"
            "  Windows: choco install poppler OR download from https://github.com/oschwartz10612/poppler-windows/releases\n"
            "  Linux: apt-get install poppler-utils\n"
            "  Mac: brew install poppler"
        )
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Convert PDF to images
    images = convert_from_path(
        pdf_path,
        dpi=dpi,
        fmt='PNG'
    )
    
    return images


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """
    Convert PIL Image to base64 string.
    
    Args:
        image: PIL Image object
        format: Image format (PNG, JPEG)
        
    Returns:
        Base64 encoded string
    """
    buffer = BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')


def pdf_to_base64_images(pdf_path: str, dpi: int = 200) -> List[Tuple[str, int]]:
    """
    Convert PDF to list of base64 encoded images.
    
    Args:
        pdf_path: Path to PDF file
        dpi: Resolution for conversion
        
    Returns:
        List of tuples (base64_string, page_number)
    """
    images = pdf_to_images(pdf_path, dpi)
    result = []
    
    for i, img in enumerate(images, start=1):
        base64_str = image_to_base64(img)
        result.append((base64_str, i))
        
    return result


def get_pdf_page_count(pdf_path: str) -> int:
    """Get the number of pages in a PDF without full conversion"""
    images = pdf_to_images(pdf_path, dpi=72)  # Low DPI for speed
    return len(images)


if __name__ == "__main__":
    # Test the module
    import sys
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        print(f"Processing: {pdf_path}")
        images = pdf_to_images(pdf_path)
        print(f"Converted {len(images)} pages")
        for i, img in enumerate(images, 1):
            print(f"  Page {i}: {img.size}")
    else:
        print("Usage: python pdf_processor.py <path_to_pdf>")
