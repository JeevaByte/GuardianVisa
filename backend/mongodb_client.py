"""
MongoDB async client for GuardianVisa.
All collections live in the "guardianvisa" database.
Gracefully falls back to empty results when MongoDB is unreachable.
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

log = logging.getLogger(__name__)

MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "guardianvisa"

_client: Optional[AsyncIOMotorClient] = None
_mongo_available: bool = True


def get_client() -> Optional[AsyncIOMotorClient]:
    global _client, _mongo_available
    if _client is None:
        try:
            _client = AsyncIOMotorClient(MONGODB_URI)
        except Exception as exc:
            log.warning("MongoDB connection failed (%s); running without database", exc)
            _mongo_available = False
            _client = None
    return _client


def get_db():
    client = get_client()
    if client is None:
        return None
    return client[DB_NAME]


# ---------------------------------------------------------------------------
# Student profiles
# ---------------------------------------------------------------------------

async def get_student_profile(student_id: str) -> Optional[dict]:
    """Return the student document or None if not found / unavailable."""
    if not _mongo_available:
        return None
    try:
        db = get_db()
        if db is None:
            return None
        doc = await db.students.find_one({"student_id": student_id}, {"_id": 0})
        return doc
    except Exception as exc:
        log.warning("get_student_profile failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Visa rules
# ---------------------------------------------------------------------------

async def get_visa_rules(visa_type: str) -> Optional[dict]:
    """Return visa-rule document for the given visa type (e.g. 'Tier 4')."""
    if not _mongo_available:
        return None
    try:
        db = get_db()
        if db is None:
            return None
        doc = await db.visa_rules.find_one({"visa_type": visa_type}, {"_id": 0})
        return doc
    except Exception as exc:
        log.warning("get_visa_rules failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Work logs
# ---------------------------------------------------------------------------

async def get_work_logs(student_id: str, week_start: str) -> list:
    """
    Return work-log entries for a student starting from *week_start* (ISO date).
    Returns an empty list if nothing is found or database is unavailable.
    """
    if not _mongo_available:
        return []
    try:
        db = get_db()
        if db is None:
            return []
        cursor = db.work_logs.find(
            {"student_id": student_id, "week_start": {"$gte": week_start}},
            {"_id": 0},
        )
        return await cursor.to_list(length=100)
    except Exception as exc:
        log.warning("get_work_logs failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Scam patterns
# ---------------------------------------------------------------------------

async def search_scam_patterns(keywords: list[str]) -> list:
    """
    Full-text / keyword search against known scam patterns.
    Falls back gracefully if MongoDB is unavailable.
    """
    if not _mongo_available:
        return []
    try:
        db = get_db()
        if db is None:
            return []
        try:
            cursor = db.scam_patterns.find(
                {"$text": {"$search": " ".join(keywords)}},
                {"_id": 0, "score": {"$meta": "textScore"}},
            ).sort([("score", {"$meta": "textScore"})])
            return await cursor.to_list(length=20)
        except Exception:
            pattern = "|".join(keywords)
            cursor = db.scam_patterns.find(
                {"description": {"$regex": pattern, "$options": "i"}},
                {"_id": 0},
            )
            return await cursor.to_list(length=20)
    except Exception as exc:
        log.warning("search_scam_patterns failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Emergency resources
# ---------------------------------------------------------------------------

async def get_emergency_resources(city: str) -> list:
    """Return support resources (legal aid, housing, mental-health) for a city."""
    if not _mongo_available:
        return []
    try:
        db = get_db()
        if db is None:
            return []
        cursor = db.emergency_resources.find(
            {"city": {"$regex": city, "$options": "i"}},
            {"_id": 0},
        )
        return await cursor.to_list(length=50)
    except Exception as exc:
        log.warning("get_emergency_resources failed: %s", exc)
        return []
