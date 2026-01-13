#!/usr/bin/env python
"""
Utility script to list available Gemini models.
Run this to verify your API key works and see available models.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not set in .env file")
    sys.exit(1)

print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
print("\nListing available models...\n")

try:
    from google import genai
    
    client = genai.Client(api_key=api_key)
    
    # List all models
    models = client.models.list()
    
    print("Available models supporting generateContent:")
    print("-" * 60)
    
    for model in models:
        # Filter for models that support generateContent
        if hasattr(model, 'supported_generation_methods'):
            if 'generateContent' in model.supported_generation_methods:
                print(f"  {model.name}")
        else:
            # If we can't check, just print all models
            print(f"  {model.name}")
    
    print("-" * 60)
    print("\nRecommended for this project: gemini-2.5-flash")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
