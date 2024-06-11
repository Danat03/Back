import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.user.user_handler import user_router
from api.auth.auth_handler import auth_router
from api.message.message_handler import message_router
from db.redis import get_redis_auth_pool, get_redis_messages_pool

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_api_router = APIRouter()
main_api_router.include_router(user_router, prefix="/user", tags=["user"])
main_api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
main_api_router.include_router(message_router, prefix="/messages", tags=["messages"])
app.include_router(main_api_router)

@app.on_event("startup")
async def startup_event():
    await get_redis_auth_pool()
    await get_redis_messages_pool()

@app.on_event("shutdown")
async def shutdown_event():
    redis_pool_auth = await get_redis_auth_pool()
    redis_pool_message = await get_redis_messages_pool()
    await redis_pool_auth.close()
    await redis_pool_message.close()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000
    )
    