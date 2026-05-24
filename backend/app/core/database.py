from __future__ import annotations

import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

log = logging.getLogger(__name__)


class MongoManager:
    def __init__(self) -> None:
        self._client: Optional[AsyncIOMotorClient] = None

    def connect(self) -> None:
        if self._client is None:
            self._client = AsyncIOMotorClient(settings.mongodb_uri)

    async def ping(self) -> bool:
        try:
            self.connect()
            await self._client.admin.command("ping")
            return True
        except Exception as exc:
            log.warning("MongoDB unavailable: %s", exc)
            return False

    @property
    def db(self) -> AsyncIOMotorDatabase | None:
        if self._client is None:
            self.connect()
        return self._client[settings.mongodb_db_name] if self._client else None

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None


mongo_manager = MongoManager()

