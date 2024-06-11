import json
from typing import List
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Message
from settings import ekb_timezone

async def save_message(
    user_id: str,
    content: str,
    username: str,
    db: AsyncSession,
    redis_pool_messages: Redis,
):
    new_message = Message(user_id=user_id, content=content)
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    created_at_with_tz = new_message.created_at.astimezone(ekb_timezone)
    message_data = {
        "id": new_message.id,
        "user_id": str(user_id),
        "username": username,
        "content": content,
        "created_at": created_at_with_tz.isoformat(),
    }
    key = "chat_messages"
    await redis_pool_messages.rpush(key, json.dumps(message_data, ensure_ascii=False))
    await redis_pool_messages.ltrim(key, 0, 99)

async def get_messages(
    redis_pool_messages: Redis, start: int = -20, count: int = 20
) -> List[dict]:
    key = "chat_messages"
    end = start + count - 1
    messages = await redis_pool_messages.lrange(key, start, end)
    return [json.loads(message) for message in messages]
