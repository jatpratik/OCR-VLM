"""
MongoDB storage module for valuation reports.
Uses Motor (async MongoDB driver) for FastAPI integration.
"""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# MongoDB connection
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_mongodb_uri() -> str:
    """Get MongoDB URI from environment"""
    return os.getenv("MONGODB_URI", "mongodb://localhost:27017")


def get_database_name() -> str:
    """Get database name from environment"""
    return os.getenv("MONGODB_DB", "valuation_reports")


async def connect_db() -> AsyncIOMotorDatabase:
    """Connect to MongoDB and return database instance"""
    global _client, _db
    
    if _db is not None:
        return _db
    
    uri = get_mongodb_uri()
    db_name = get_database_name()
    
    _client = AsyncIOMotorClient(uri)
    _db = _client[db_name]
    
    # Create indexes
    await _db.reports.create_index("applicationNumber")
    await _db.reports.create_index("createdAt")
    
    return _db


async def close_db():
    """Close MongoDB connection"""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None


async def get_db() -> AsyncIOMotorDatabase:
    """Get database instance, connecting if necessary"""
    if _db is None:
        return await connect_db()
    return _db


# CRUD Operations

async def create_report(report_data: Dict[str, Any], source_pdf: str) -> str:
    """
    Create a new valuation report in the database.
    
    Args:
        report_data: Extracted report data
        source_pdf: Original PDF filename
        
    Returns:
        Inserted document ID as string
    """
    db = await get_db()
    
    # Add metadata
    document = {
        **report_data,
        "_metadata": {
            "sourcePdf": source_pdf,
            "extractedAt": datetime.utcnow(),
            "version": "1.0"
        },
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await db.reports.insert_one(document)
    return str(result.inserted_id)


async def get_report(report_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a single report by ID.
    
    Args:
        report_id: MongoDB document ID
        
    Returns:
        Report document or None if not found
    """
    db = await get_db()
    
    try:
        doc = await db.reports.find_one({"_id": ObjectId(report_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    except Exception:
        return None


async def get_all_reports(
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "createdAt",
    sort_order: int = -1
) -> List[Dict[str, Any]]:
    """
    Get all reports with pagination.
    
    Args:
        skip: Number of documents to skip
        limit: Maximum documents to return
        sort_by: Field to sort by
        sort_order: 1 for ascending, -1 for descending
        
    Returns:
        List of report documents
    """
    db = await get_db()
    
    cursor = db.reports.find().sort(sort_by, sort_order).skip(skip).limit(limit)
    
    reports = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        reports.append(doc)
    
    return reports


async def count_reports() -> int:
    """Get total count of reports"""
    db = await get_db()
    return await db.reports.count_documents({})


async def update_report(report_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update a report by ID.
    
    Args:
        report_id: MongoDB document ID
        update_data: Fields to update
        
    Returns:
        True if updated, False if not found
    """
    db = await get_db()
    
    update_data["updatedAt"] = datetime.utcnow()
    
    try:
        result = await db.reports.update_one(
            {"_id": ObjectId(report_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    except Exception:
        return False


async def delete_report(report_id: str) -> bool:
    """
    Delete a report by ID.
    
    Args:
        report_id: MongoDB document ID
        
    Returns:
        True if deleted, False if not found
    """
    db = await get_db()
    
    try:
        result = await db.reports.delete_one({"_id": ObjectId(report_id)})
        return result.deleted_count > 0
    except Exception:
        return False


async def search_reports(
    application_number: Optional[str] = None,
    applicant_name: Optional[str] = None,
    post_code: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search reports by various criteria.
    
    Args:
        application_number: Partial match on application number
        applicant_name: Partial match on applicant name
        post_code: Partial match on post code
        
    Returns:
        List of matching reports
    """
    db = await get_db()
    
    query = {}
    
    if application_number:
        query["applicationNumber"] = {"$regex": application_number, "$options": "i"}
    if applicant_name:
        query["applicantName"] = {"$regex": applicant_name, "$options": "i"}
    if post_code:
        query["postCode"] = {"$regex": post_code, "$options": "i"}
    
    cursor = db.reports.find(query).limit(100)
    
    reports = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        reports.append(doc)
    
    return reports
