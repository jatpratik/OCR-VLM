"""
FastAPI application for OCR Valuation Report Extraction.
Provides REST API endpoints for PDF extraction and report management.
"""

import os
import tempfile
import shutil
from typing import Optional, List
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import storage and extraction modules
from src.storage.mongodb_storage import (
    connect_db, close_db, get_db,
    create_report, get_report, get_all_reports,
    count_reports, delete_report, search_reports
)
from src.storage.json_storage import save_extraction
from src.extractors.vision_extractor import extract_from_pdf

# Create FastAPI app
app = FastAPI(
    title="Valuation Report OCR API",
    description="Extract and manage data from UK Buy to Let Mortgage Valuation Report PDFs",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API responses
class ReportSummary(BaseModel):
    id: str
    applicationNumber: Optional[str] = None
    applicantName: Optional[str] = None
    propertyAddress: Optional[str] = None
    postCode: Optional[str] = None
    createdAt: Optional[str] = None


class ExtractResponse(BaseModel):
    success: bool
    message: str
    report_id: Optional[str] = None
    fields_extracted: int = 0


class ReportListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    reports: List[dict]


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    try:
        await connect_db()
        print("✓ Connected to MongoDB")
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        print("  Extraction will still work, but reports won't be stored in database.")


@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    await close_db()
    print("✓ MongoDB connection closed")


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db = await get_db()
        await db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status
    }


# Extract endpoint
@app.post("/extract", response_model=ExtractResponse)
async def extract_document(
    file: UploadFile = File(...),
    model: str = Query(default="gemini-2.5-flash", description="LLM model to use"),
    save_json: bool = Query(default=True, description="Also save as JSON file")
):
    """
    Upload a PDF and extract valuation report data.
    
    - Extracts data using Gemini Vision LLM
    - Stores result in MongoDB
    - Optionally saves JSON backup to output/
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Save uploaded file to temp location
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Write uploaded file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract data from PDF
        print(f"Extracting from: {file.filename}")
        extracted_data = extract_from_pdf(
            temp_path,
            model_name=model,
            verbose=True
        )
        
        # Count extracted fields
        def count_fields(obj):
            count = 0
            for k, v in obj.items() if isinstance(obj, dict) else []:
                if isinstance(v, dict):
                    count += count_fields(v)
                elif v is not None:
                    count += 1
            return count
        
        field_count = count_fields(extracted_data)
        
        # Save to MongoDB
        report_id = None
        try:
            report_id = await create_report(extracted_data, file.filename)
            print(f"✓ Saved to MongoDB: {report_id}")
        except Exception as e:
            print(f"✗ MongoDB save failed: {e}")
        
        # Optionally save JSON backup
        if save_json:
            json_path = save_extraction(
                extracted_data,
                output_dir="output",
                source_pdf=file.filename
            )
            print(f"✓ JSON saved: {json_path}")
        
        return ExtractResponse(
            success=True,
            message=f"Successfully extracted {field_count} fields from {file.filename}",
            report_id=report_id,
            fields_extracted=field_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temp files
        shutil.rmtree(temp_dir, ignore_errors=True)


# List all reports
@app.get("/reports", response_model=ReportListResponse)
async def list_reports(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100)
):
    """
    List all extracted reports with pagination.
    """
    try:
        reports = await get_all_reports(skip=skip, limit=limit)
        total = await count_reports()
        
        return ReportListResponse(
            total=total,
            skip=skip,
            limit=limit,
            reports=reports
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get single report
@app.get("/reports/{report_id}")
async def get_single_report(report_id: str):
    """
    Get a single report by ID.
    """
    report = await get_report(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


# Delete report
@app.delete("/reports/{report_id}")
async def delete_single_report(report_id: str):
    """
    Delete a report by ID.
    """
    deleted = await delete_report(report_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {"success": True, "message": "Report deleted"}


# Search reports
@app.get("/reports/search/")
async def search_reports_endpoint(
    application_number: Optional[str] = None,
    applicant_name: Optional[str] = None,
    post_code: Optional[str] = None
):
    """
    Search reports by application number, applicant name, or post code.
    """
    if not any([application_number, applicant_name, post_code]):
        raise HTTPException(
            status_code=400, 
            detail="At least one search parameter required"
        )
    
    reports = await search_reports(
        application_number=application_number,
        applicant_name=applicant_name,
        post_code=post_code
    )
    
    return {
        "count": len(reports),
        "reports": reports
    }


# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
