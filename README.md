# OCR Valuation Report Extraction

Python-based system for extracting structured data from UK Buy to Let Mortgage Valuation Report PDFs using Vision LLMs.

## Quick Start

### Option 1: Using Ollama (FREE, Local, No Limits) ⭐ Recommended

```bash
# 1. Install Ollama from https://ollama.ai
# 2. Start Ollama and pull a vision model
ollama serve
ollama pull llava

# 3. Run extraction
python run.py --input "data/All yes fields (1).pdf" --backend ollama
```

### Option 2: Using Google Gemini (API, has quota limits)

```bash
# 1. Set up API key
copy .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 2. Run extraction
python run.py --input "data/All yes fields (1).pdf"
```

## Installation

```bash
pip install -r requirements.txt
```

**For PDF processing, install Poppler:**
- Windows: `choco install poppler` or download from [GitHub](https://github.com/oschwartz10612/poppler-windows/releases)
- Linux: `apt-get install poppler-utils`
- Mac: `brew install poppler`

## Usage Examples

```bash
# Free local extraction with Ollama
python run.py -i "data/report.pdf" --backend ollama

# With specific Ollama model
python run.py -i "data/report.pdf" --backend ollama --model llava:13b

# Using Gemini (requires API key)
python run.py -i "data/report.pdf" --backend gemini

# Custom output location
python run.py -i "data/report.pdf" -o "output/result.json" --backend ollama
```

## Output

Extracted data is saved as JSON in the `output/` directory, matching the schema structure.
