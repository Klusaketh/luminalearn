import logging
import time
from typing import Any

from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger("luminalearn.redis")


class InMemoryRedisFallback:
    """In-memory Redis mock store for development when Redis server is unreachable."""
    def __init__(self) -> None:
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

    def remaining_ttl(self, key: str) -> int | None:
        """Seconds until `key` expires (None when absent or already expired)."""
        entry = self._store.get(key)
        if entry is None or entry[1] is None:
            return None
        remaining = int(entry[1] - time.time())
        return remaining if remaining > 0 else None


_real_redis: Redis = Redis.from_url(
    settings.REDIS_URI,
    encoding="utf-8",
    decode_responses=True,
    socket_connect_timeout=0.2,
    socket_timeout=0.2,
)

# After a failure, skip the real server for this long instead of paying the
# connect timeout on every call while Redis is down.
REDIS_RETRY_AFTER_SECONDS = 30.0


class RedisClientWrapper:
    """
    Resilient Redis wrapper providing graceful in-memory fallback.

    Every write lands in the in-memory store; the real server is used whenever it is
    reachable. While the server is suspended, touched keys are remembered and written
    back on recovery so revoked tokens or spent OTPs cannot reappear from stale state.
    """
    def __init__(self) -> None:
        self._fallback = InMemoryRedisFallback()
        self._suspended_until = 0.0
        self._unsynced_keys: set[str] = set()

    def _suspend(self, exc: Exception) -> None:
        if time.monotonic() >= self._suspended_until:
            logger.debug("Redis unreachable (%s); serving from in-memory fallback.", exc)
        self._suspended_until = time.monotonic() + REDIS_RETRY_AFTER_SECONDS

    async def _real_available(self) -> bool:
        if time.monotonic() < self._suspended_until:
            return False
        if self._unsynced_keys:
            return await self._resync()
        return True

    async def _resync(self) -> bool:
        """Replays keys changed during the outage onto the recovered server."""
        try:
            for key in sorted(self._unsynced_keys):
                value = await self._fallback.get(key)
                ttl = self._fallback.remaining_ttl(key)
                if value is not None and ttl is not None:
                    await _real_redis.set(key, value, ex=ttl)
                else:
                    await _real_redis.delete(key)
                self._unsynced_keys.discard(key)
        except Exception as exc:  # noqa: BLE001 - any Redis/socket/event-loop failure degrades to memory
            self._suspend(exc)
            return False
        return True

    async def get(self, key: str) -> str | None:
        if await self._real_available():
            try:
                val = await _real_redis.get(key)
                if val is not None:
                    return val.decode("utf-8") if isinstance(val, bytes) else str(val)
            except Exception as exc:  # noqa: BLE001 - any Redis/socket/event-loop failure degrades to memory
                self._suspend(exc)
        return await self._fallback.get(key)

    async def setex(self, key: str, time_seconds: int, value: str) -> None:
        if await self._real_available():
            try:
                await _real_redis.set(key, value, ex=time_seconds)
            except Exception as exc:  # noqa: BLE001 - any Redis/socket/event-loop failure degrades to memory
                self._suspend(exc)
                self._unsynced_keys.add(key)
        else:
            self._unsynced_keys.add(key)
        await self._fallback.setex(key, time_seconds, value)

    async def delete(self, key: str) -> int:
        if await self._real_available():
            try:
                await _real_redis.delete(key)
            except Exception as exc:  # noqa: BLE001 - any Redis/socket/event-loop failure degrades to memory
                self._suspend(exc)
                self._unsynced_keys.add(key)
        else:
            self._unsynced_keys.add(key)
        return await self._fallback.delete(key)


# Global Resilient Redis Client Singleton
redis_client: Any = RedisClientWrapper()


async def get_redis_client() -> Any:
    """FastAPI Dependency yielding Resilient Redis Connection."""
    return redis_client
