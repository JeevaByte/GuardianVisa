from __future__ import annotations

from app.repositories.memory_repository import MemoryRepository


class MemoryService:
    def __init__(self, repo: MemoryRepository):
        self.repo = repo

    async def get_context(self, user_id: str) -> dict:
        conversations = await self.repo.get_recent_conversation(user_id=user_id, limit=16)
        memories = await self.repo.list_student_memory(user_id=user_id, limit=12)
        compressed_summary = self._compress_conversation(conversations)
        return {
            "recent_conversations": conversations,
            "compressed_conversation": compressed_summary,
            "memory_highlights": memories,
        }

    async def store_user_message(self, user_id: str, message: str) -> None:
        await self.repo.save_conversation(user_id=user_id, message=message, role="user")

    async def store_agent_message(self, user_id: str, message: str) -> None:
        await self.repo.save_conversation(user_id=user_id, message=message, role="agent")

    async def store_memory_summary(self, user_id: str, summary: str, tags: list[str]) -> None:
        await self.repo.save_student_memory(user_id=user_id, summary=summary, tags=tags)

    async def save_trace(self, user_id: str, trace: dict) -> None:
        await self.repo.save_trace(user_id, trace)

    def _compress_conversation(self, conversations: list[dict]) -> str:
        if not conversations:
            return ""
        compressed = []
        for item in conversations[-8:]:
            msg = item.get("message", "")
            if len(msg) > 120:
                msg = msg[:117] + "..."
            compressed.append(f"{item.get('role', 'unknown')}: {msg}")
        return " | ".join(compressed)

