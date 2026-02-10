import json
from typing import Any, Optional
import redis.asyncio as redis
from backend.utils.config import settings
from backend.utils.logger import logger


class RedisCache:
    """Async Redis cache for risk scores and analysis results."""

    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def connect(self):
        """Establish Redis connection."""
        self._redis = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        logger.info("Redis cache connected")

    async def disconnect(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            logger.info("Redis cache disconnected")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._redis:
            return None
        value = await self._redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with optional TTL in seconds."""
        if not self._redis:
            return
        serialized = json.dumps(value) if not isinstance(value, str) else value
        if ttl:
            await self._redis.setex(key, ttl, serialized)
        else:
            await self._redis.set(key, serialized)

    async def delete(self, key: str):
        """Delete key from cache."""
        if self._redis:
            await self._redis.delete(key)

    async def flush_pattern(self, pattern: str):
        """Delete all keys matching pattern."""
        if not self._redis:
            return
        async for key in self._redis.scan_iter(match=pattern):
            await self._redis.delete(key)


cache = RedisCache()
