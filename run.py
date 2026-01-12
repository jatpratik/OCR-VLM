#!/usr/bin/env python
"""
Valuation Report OCR Extraction - Main Entry Point

Usage:
    # Using Gemini (requires API key, has quota limits)
    python run.py --input "data/sample.pdf"
    
    # Using Ollama (FREE, local, no limits)
    python run.py --input "data/sample.pdf" --backend ollama
"""

import argparse
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv


def main():
    """Main entry point for the extraction pipeline."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Extract data from UK Buy to Let Mortgage Valuation Report PDFs"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the input PDF file"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file path (default: output/<input_filename>.json)"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory (default: output)"
    )
    parser.add_argument(
        "--backend", "-b",
        choices=["gemini", "ollama"],
        default="gemini",
        help="Extraction backend: 'gemini' (API) or 'ollama' (local, FREE)"
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model to use (gemini: gemini-2.0-flash, ollama: llava)"
    )
    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434",
        help="Ollama API URL (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Set default model based on backend
    if args.model is None:
        args.model = "llava" if args.backend == "ollama" else "gemini-2.0-flash"
    
    # Check for API key if using Gemini
    if args.backend == "gemini" and not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set for Gemini backend.")
        print("\nOptions:")
        print("  1. Set GOOGLE_API_KEY in .env file")
        print("  2. Use FREE local Ollama: python run.py -i input.pdf --backend ollama")
        sys.exit(1)
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)
    
    try:
        # Run extraction
        if not args.quiet:
            print("=" * 60)
            print("Valuation Report OCR Extraction")
            print(f"Backend: {args.backend.upper()}")
            print("=" * 60)
        
        if args.backend == "ollama":
            from src.extractors.ollama_extractor import extract_from_pdf_ollama
            extracted_data = extract_from_pdf_ollama(
                args.input,
                model_name=args.model,
                base_url=args.ollama_url,
                verbose=not args.quiet
            )
        else:
            from src.extractors.vision_extractor import extract_from_pdf
            extracted_data = extract_from_pdf(
                args.input,
                model_name=args.model,
                verbose=not args.quiet
            )
        
        # Import storage module
        from src.storage.json_storage import save_extraction
        
        # Determine output path
        if args.output:
            output_dir = os.path.dirname(args.output) or args.output_dir
            filename = Path(args.output).stem
        else:
            output_dir = args.output_dir
            filename = None
        
        # Save results
        output_path = save_extraction(
            extracted_data,
            output_dir=output_dir,
            filename=filename,
            source_pdf=args.input
        )
        
        if not args.quiet:
            print("=" * 60)
            print(f"SUCCESS! Output saved to: {output_path}")
            print("=" * 60)
        else:
            print(output_path)
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
