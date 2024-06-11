from typing import Optional
from redis.asyncio import Redis

from settings import REDIS_URL

redis_pool_auth: Optional[Redis] = None
redis_pool_messages: Optional[Redis] = None

async def get_redis_auth_pool() -> Redis:
    return await Redis.from_url(
        REDIS_URL, encoding="utf-8", decode_responses=True, db=0
    )

async def get_redis_messages_pool() -> Redis:
    return await Redis.from_url(
        REDIS_URL, encoding="utf-8", decode_responses=True, db=1
    )