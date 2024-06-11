from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from api.auth.dependencies import check_session, get_cookie_or_token
from db.session import get_db
from db.redis import get_redis_auth_pool, get_redis_messages_pool
from api.user.actions import _get_user_by_id
from api.message.websocket.action import handle_messages, handle_websocket_connect, handle_websocket_disconnect

message_router = APIRouter()

@message_router.websocket("/ws")
async def websocket_endpoint(
        *,
        websocket: WebSocket,
        cookie_or_token: str = Depends(get_cookie_or_token),
        redis_messages: Redis = Depends(get_redis_messages_pool),
        redis_auth: Redis = Depends(get_redis_auth_pool),
        session: AsyncSession = Depends(get_db)
):
    user = None
    if cookie_or_token is None:
        await websocket.close(code=4001, reason="No token provided")
        return
    user_id, token_valid = await check_session(cookie_or_token, redis_auth)
    if not token_valid:
        await websocket.close(code=4001, reason="No token valid")
        return
    try:
        while True:
            user = await _get_user_by_id(session=session, user_id=user_id)
            if not user:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            await handle_websocket_connect(user, websocket, session, redis_messages)
            await handle_messages(websocket, user, session, redis_messages)
    except WebSocketDisconnect:
        await handle_websocket_disconnect(user, websocket, session)
