import asyncio
import json
import logging
import settings
import jwt
from datetime import datetime
from jwt import ExpiredSignatureError
from typing import Tuple, Union, Optional
from uuid import UUID
from fastapi import Depends, Cookie, Query, HTTPException, status, Request, WebSocketException
from starlette.websockets import WebSocketState
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis

from db.redis import get_redis_auth_pool

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def verify_token(
    request: Request, redis: Redis = Depends(get_redis_auth_pool)
) -> UUID:
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = UUID(payload.get("sub"))
        if user_id is None or not await redis.get(f"user_id:{user_id}"):
            raise HTTPException(
                status_code=401, detail="Authentication failed or token expired"
            )
        return user_id
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except (jwt.PyJWTError, ValueError) as e:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    
async def check_session(token: str, redis_auth: Redis) -> Tuple[Optional[UUID], bool]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = UUID(payload.get("sub"))
        if user_id is None:
            return None, False

        user_key = f"user_id:{user_id}"
        session_data = await redis_auth.get(user_key)
        if session_data is None:
            return None, False

        session_info = json.loads(session_data)
        expiration_time_str = session_info['exp']
        expiration_time = datetime.strptime(expiration_time_str, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=settings.ekb_timezone)
        current_time = datetime.now(settings.ekb_timezone)

        if current_time > expiration_time:
            await redis_auth.delete(user_key)
            return None, False
        return user_id, True
    except (jwt.PyJWTError, ValueError):
        return None, False
    
async def maintain_session(websocket, token, redis_auth):
    while True:
        await asyncio.sleep(5)
        _, token_valid = await check_session(token, redis_auth)
        if not token_valid:
            if websocket.application_state != WebSocketState.DISCONNECTED:
                await websocket.close(code=4001, reason="Connections refused.")
                break

async def get_cookie_or_token(
    session: Union[str, None] = Cookie(default=None),
    token: Union[str, None] = Query(default=None),
):
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token
    