from __future__ import annotations

import hashlib
from pathlib import Path

from app.repositories.memory_repository import MemoryRepository


class RAGService:
    def __init__(self, repo: MemoryRepository):
        self.repo = repo

    async def ingest_document(self, source_path: str, source_type: str = "policy") -> int:
        content = Path(source_path).read_text(encoding="utf-8", errors="ignore")
        chunks = self._chunk_text(content)
        for idx, chunk in enumerate(chunks):
            await self.repo.save_document_chunk(
                {
                    "chunk_id": f"{Path(source_path).stem}_{idx}",
                    "source": source_path,
                    "source_type": source_type,
                    "text": chunk,
                    "embedding": self._embed(chunk),
                }
            )
        return len(chunks)

    async def retrieve(self, query: str, limit: int = 5) -> list[dict]:
        docs = await self.repo.search_documents(query_embedding=self._embed(query), limit=limit)
        return [
            {
                "text": d.get("text", ""),
                "source": d.get("source", "unknown"),
                "citation": f"{d.get('source', 'unknown')}#{d.get('chunk_id', 'chunk')}",
                "similarity": d.get("similarity", 0.0),
            }
            for d in docs
        ]

    @staticmethod
    def _chunk_text(text: str, size: int = 900, overlap: int = 120) -> list[str]:
        if not text:
            return []
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + size, len(text))
            chunks.append(text[start:end])
            if end == len(text):
                break
            start = end - overlap
        return chunks

    @staticmethod
    def _embed(text: str, dim: int = 48) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        expanded = (digest * ((dim // len(digest)) + 1))[:dim]
        return [round((byte / 255.0) * 2 - 1, 6) for byte in expanded]

