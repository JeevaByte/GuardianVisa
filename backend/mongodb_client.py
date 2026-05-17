"""
MongoDB async client for GuardianVisa.
All collections live in the "guardianvisa" database.
"""

import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "guardianvisa"

# Module-level client — created once, reused across requests.
_client: Optional[AsyncIOMotorClient] = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGODB_URI)
    return _client


def get_db():
    return get_client()[DB_NAME]


# ---------------------------------------------------------------------------
# Student profiles
# ---------------------------------------------------------------------------

async def get_student_profile(student_id: str) -> Optional[dict]:
    """Return the student document or None if not found."""
    db = get_db()
    doc = await db.students.find_one({"student_id": student_id}, {"_id": 0})
    return doc


# ---------------------------------------------------------------------------
# Visa rules
# ---------------------------------------------------------------------------

async def get_visa_rules(visa_type: str) -> Optional[dict]:
    """Return visa-rule document for the given visa type (e.g. 'Tier 4')."""
    db = get_db()
    doc = await db.visa_rules.find_one({"visa_type": visa_type}, {"_id": 0})
    return doc


# ---------------------------------------------------------------------------
# Work logs
# ---------------------------------------------------------------------------

async def get_work_logs(student_id: str, week_start: str) -> list:
    """
    Return work-log entries for a student starting from *week_start* (ISO date).
    Returns an empty list if nothing is found.
    """
    db = get_db()
    cursor = db.work_logs.find(
        {"student_id": student_id, "week_start": {"$gte": week_start}},
        {"_id": 0},
    )
    return await cursor.to_list(length=100)


# ---------------------------------------------------------------------------
# Scam patterns
# ---------------------------------------------------------------------------

async def search_scam_patterns(keywords: list[str]) -> list:
    """
    Full-text / keyword search against known scam patterns.
    Falls back gracefully if a text index is not configured.
    """
    db = get_db()
    try:
        cursor = db.scam_patterns.find(
            {"$text": {"$search": " ".join(keywords)}},
            {"_id": 0, "score": {"$meta": "textScore"}},
        ).sort([("score", {"$meta": "textScore"})])
        return await cursor.to_list(length=20)
    except Exception:
        # If text index doesn't exist, fall back to a simple regex search.
        pattern = "|".join(keywords)
        cursor = db.scam_patterns.find(
            {"description": {"$regex": pattern, "$options": "i"}},
            {"_id": 0},
        )
        return await cursor.to_list(length=20)


# ---------------------------------------------------------------------------
# Emergency resources
# ---------------------------------------------------------------------------

async def get_emergency_resources(city: str) -> list:
    """Return support resources (legal aid, housing, mental-health) for a city."""
    db = get_db()
    cursor = db.emergency_resources.find(
        {"city": {"$regex": city, "$options": "i"}},
        {"_id": 0},
    )
    return await cursor.to_list(length=50)
