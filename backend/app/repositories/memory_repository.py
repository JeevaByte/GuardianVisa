from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.core.database import mongo_manager


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryRepository:
    collection_names = {
        "users": "users",
        "student_memory": "student_memory",
        "risk_history": "risk_history",
        "alerts": "alerts",
        "conversations": "conversations",
        "emergency_cases": "emergency_cases",
        "scam_reports": "scam_reports",
        "planner_traces": "planner_traces",
        "monitor_runs": "monitor_runs",
        "documents": "documents",
    }

    async def upsert_user(self, user_id: str, payload: dict[str, Any]) -> None:
        db = mongo_manager.db
        if db is None:
            return
        await db[self.collection_names["users"]].update_one(
            {"user_id": user_id},
            {"$set": {**payload, "updated_at": utc_now_iso()}, "$setOnInsert": {"created_at": utc_now_iso()}},
            upsert=True,
        )

    async def list_users(self, limit: int = 50) -> list[dict[str, Any]]:
        db = mongo_manager.db
        if db is None:
            return []
        cursor = db[self.collection_names["users"]].find({}, {"_id": 0}).limit(limit)
        return await cursor.to_list(length=limit)

    async def save_conversation(self, user_id: str, message: str, role: str, compressed: bool = False) -> None:
        db = mongo_manager.db
        if db is None:
            return
        await db[self.collection_names["conversations"]].insert_one(
            {
                "user_id": user_id,
                "role": role,
                "message": message,
                "compressed": compressed,
                "created_at": utc_now_iso(),
            }
        )

    async def get_recent_conversation(self, user_id: str, limit: int = 12) -> list[dict[str, Any]]:
        db = mongo_manager.db
        if db is None:
            return []
        cursor = (
            db[self.collection_names["conversations"]]
            .find({"user_id": user_id}, {"_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        docs.reverse()
        return docs

    async def save_student_memory(self, user_id: str, summary: str, tags: list[str]) -> None:
        db = mongo_manager.db
        if db is None:
            return
        await db[self.collection_names["student_memory"]].insert_one(
            {"user_id": user_id, "summary": summary, "tags": tags, "created_at": utc_now_iso()}
        )

    async def list_student_memory(self, user_id: str, limit: int = 20) -> list[dict[str, Any]]:
        db = mongo_manager.db
        if db is None:
            return []
        cursor = (
            db[self.collection_names["student_memory"]]
            .find({"user_id": user_id}, {"_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def save_risk(self, user_id: str, risk_payload: dict[str, Any]) -> None:
        db = mongo_manager.db
        if db is None:
            return
        await db[self.collection_names["risk_history"]].insert_one(
            {"user_id": user_id, **risk_payload, "created_at": utc_now_iso()}
        )

    async def list_open_alerts(self, user_id: str | None = None) -> list[dict[str, Any]]:
        db = mongo_manager.db
        if db is None:
            return []
        query: dict[str, Any] = {"resolved": {"$ne": True}}
        if user_id:
            query["user_id"] = user_id
        cursor = db[self.collection_names["alerts"]].find(query, {"_id": 0}).sort("created_at", -1)
        return await cursor.to_list(length=100)

    async def create_alert(self, user_id: str, severity: str, message: str, metadata: dict[str, Any] | None = None) -> dict:
        db = mongo_manager.db
        alert_doc = {
            "id": f"alt_{abs(hash((user_id, message, utc_now_iso()))) % 10_000_000}",
            "user_id": user_id,
            "severity": severity,
            "message": message,
            "metadata": metadata or {},
            "resolved": False,
            "created_at": utc_now_iso(),
        }
        if db is not None:
            await db[self.collection_names["alerts"]].insert_one(alert_doc)
        return alert_doc

    async def save_trace(self, user_id: str, trace: dict[str, Any]) -> None:
        db = mongo_manager.db
        if db is None:
            return
        await db[self.collection_names["planner_traces"]].insert_one(
            {"user_id": user_id, "trace": trace, "created_at": utc_now_iso()}
        )

    async def save_monitor_run(self, monitor_name: str, result: dict[str, Any]) -> None:
        db = mongo_manager.db
        if db is None:
            return
        await db[self.collection_names["monitor_runs"]].insert_one(
            {"monitor_name": monitor_name, "result": result, "created_at": utc_now_iso()}
        )

    async def save_document_chunk(self, chunk: dict[str, Any]) -> None:
        db = mongo_manager.db
        if db is None:
            return
        await db[self.collection_names["documents"]].insert_one(chunk)

    async def search_documents(self, query_embedding: list[float], limit: int = 5) -> list[dict]:
        db = mongo_manager.db
        if db is None:
            return []
        cursor = db[self.collection_names["documents"]].find({}, {"_id": 0}).limit(500)
        docs = await cursor.to_list(length=500)

        def cosine(a: list[float], b: list[float]) -> float:
            num = sum(x * y for x, y in zip(a, b))
            den_a = sum(x * x for x in a) ** 0.5
            den_b = sum(y * y for y in b) ** 0.5
            return num / (den_a * den_b) if den_a and den_b else 0.0

        scored = []
        for doc in docs:
            embedding = doc.get("embedding", [])
            if embedding:
                scored.append((cosine(query_embedding, embedding), doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [{**doc, "similarity": score} for score, doc in scored[:limit]]

