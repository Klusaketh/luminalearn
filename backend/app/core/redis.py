import time
from typing import Any

from redis.asyncio import Redis

from app.core.config import settings


class InMemoryRedisFallback:
    """In-memory Redis mock store for development when Redis server is unreachable."""
    def __init__(self):
        self._store: dict[str, tuple[str, float | None]] = {}

    async def get(self, key: str) -> str | None:
        if key in self._store:
            val, expire_at = self._store[key]
            if expire_at is not None and time.time() > expire_at:
                del self._store[key]
                return None
            return val
        return None

    async def setex(self, key: str, time_seconds: int, value: str) -> None:
        expire_at = time.time() + time_seconds
        self._store[key] = (str(value), expire_at)

    async def delete(self, key: str) -> int:
        if key in self._store:
            del self._store[key]
            return 1
        return 0


_real_redis: Redis = Redis.from_url(
    settings.REDIS_URI,
    encoding="utf-8",
    decode_responses=True,
    socket_connect_timeout=0.2,
    socket_timeout=0.2,
)


class RedisClientWrapper:
    """Resilient Redis wrapper providing graceful in-memory fallback."""
    def __init__(self):
        self._fallback = InMemoryRedisFallback()

    async def get(self, key: str) -> str | None:
        try:
            val = await _real_redis.get(key)
            if val is not None:
                return val
        except Exception:
            pass
        return await self._fallback.get(key)

    async def setex(self, key: str, time_seconds: int, value: str) -> None:
        try:
            await _real_redis.setex(key, time_seconds, value)
        except Exception:
            pass
        await self._fallback.setex(key, time_seconds, value)

    async def delete(self, key: str) -> int:
        try:
            await _real_redis.delete(key)
        except Exception:
            pass
        return await self._fallback.delete(key)


# Global Resilient Redis Client Singleton
redis_client: Any = RedisClientWrapper()


async def get_redis_client() -> Any:
    """FastAPI Dependency yielding Resilient Redis Connection."""
    return redis_client

