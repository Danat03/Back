import asyncio
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, WebSocket, WebSocketDisconnect, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

import settings
from db.session import get_db
from db.redis import get_redis_auth_pool
from api.auth.actions import authenticate_user
from api.auth.dependencies import check_session, get_cookie_or_token, maintain_session, verify_token
from api.auth.security import create_access_token

auth_router = APIRouter()

@auth_router.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    session = await create_access_token(
        user_id=user.user_id,
        expires_delta=access_token_expires,
    )
    response.set_cookie(
        key="session",
        value=session,
        httponly=True,
        secure=True,
        samesite="none"
    )
    return {"message": "Authentication successful"}

@auth_router.post("/logout")
async def logout(response: Response, request: Request, redis: Redis = Depends(get_redis_auth_pool)):
    user_id = await verify_token(request, redis)
    if user_id:
        await redis.delete(f"user_id:{user_id}")
    response.delete_cookie("session")
    return {"message": "Logged out successfully"}

@auth_router.get("/verify")
async def protected_route(request: Request, redis: Redis = Depends(get_redis_auth_pool)):
    await verify_token(request, redis)
    return True

@auth_router.websocket("/ws")
async def websocket_endpoint(
        *,
        websocket: WebSocket,
        cookie_or_token: str = Depends(get_cookie_or_token),
        redis_auth: Redis = Depends(get_redis_auth_pool)
):
    await websocket.accept()
    if cookie_or_token is None:
        await websocket.close(code=4001, reason="No token provided")
        return

    user_id, token_valid = await check_session(cookie_or_token, redis_auth)
    if not token_valid:
        await websocket.close(code=4001, reason="No token valid")
        return

    await websocket.send_json({"type": "AUTH_STATUS", "isAuthenticated": True})
    session_task = asyncio.create_task(maintain_session(websocket, cookie_or_token, redis_auth))

    try:
        while True:
            await websocket.receive_text()
            _, token_valid = await check_session(cookie_or_token, redis_auth)
            if not token_valid:
                await websocket.send_json({"type": "AUTH_STATUS", "isAuthenticated": False})
                await websocket.close(code=4001, reason="Token expired")
                break

            await websocket.send_json({"type": "message", "message": "Session is active"})
    except WebSocketDisconnect:
        session_task.cancel()
        