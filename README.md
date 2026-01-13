# OCR Valuation Report Extraction

Extract structured data from UK Buy to Let Mortgage Valuation Report PDFs using Vision LLMs.

## Quick Start

### 1. Start MongoDB (Docker)
```bash
docker-compose up -d
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
copy .env.example .env
# Edit .env with your GOOGLE_API_KEY
```

### 4. Start API Server
```bash
uvicorn src.api.main:app --reload
```

API docs available at: http://localhost:8000/docs

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/extract` | Upload PDF and extract data |
| GET | `/reports` | List all reports |
| GET | `/reports/{id}` | Get single report |
| DELETE | `/reports/{id}` | Delete report |
| GET | `/reports/search/` | Search reports |

### Extract PDF Example
```bash
curl -X POST "http://localhost:8000/extract" \
  -F "file=@data/sample.pdf" \
  -F "model=gemini-2.5-flash"
```

---

## CLI Usage

```bash
# Extract with Gemini
python run.py -i "data/report.pdf" --model gemini-2.5-flash

# Extract with Ollama (free, local)
python run.py -i "data/report.pdf" --backend ollama
```

---

## Project Structure

```
├── data/                  # Sample PDFs
├── output/                # JSON output files
├── src/
│   ├── api/               # FastAPI application
│   ├── extractors/        # PDF & LLM processing
│   ├── schemas/           # Pydantic models
│   └── storage/           # MongoDB & JSON storage
├── docker-compose.yml     # MongoDB container
└── run.py                 # CLI entry point
```

---

## Requirements

- Python 3.9+
- Docker (for MongoDB)
- Poppler (for PDF processing)
- Google API key or Ollama for extraction
