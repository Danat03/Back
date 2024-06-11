import json
import settings
import jwt
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from db.redis import get_redis_auth_pool

async def create_access_token(user_id: UUID, expires_delta: Optional[timedelta] = None):
    expire = datetime.now(settings.ekb_timezone) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {
        "sub": str(user_id),
        "exp": expire.timestamp()
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    redis = await get_redis_auth_pool()
    ttl = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    expiration_datetime_str = expire.strftime("%Y-%m-%d %H:%M:%S")
    user_key = f"user_id:{user_id}"
    await redis.delete(user_key)
    await redis.setex(
        f"user_id:{user_id}",
        ttl,
        json.dumps({"token": encoded_jwt, "user_id": str(user_id), "exp": expiration_datetime_str})
    )
    return encoded_jwt
