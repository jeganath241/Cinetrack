from redis import Redis
from typing import Optional, Any
import json
from app.core.config import settings

class RedisService:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.default_ttl = 3600  # 1 hour default cache time

    async def get_cached_data(self, key: str) -> Optional[Any]:
        """Get cached data from Redis"""
        data = self.redis.get(key)
        return json.loads(data) if data else None

    async def set_cached_data(self, key: str, data: Any, ttl: int = None) -> None:
        """Set data in Redis cache"""
        ttl = ttl or self.default_ttl
        self.redis.setex(
            key,
            ttl,
            json.dumps(data)
        )

    async def delete_cached_data(self, key: str) -> None:
        """Delete cached data from Redis"""
        self.redis.delete(key)

    async def clear_cache(self) -> None:
        """Clear all cached data"""
        self.redis.flushall()

redis_service = RedisService() 