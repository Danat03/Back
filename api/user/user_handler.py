from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from api.schemas import ShowUser, UserCreate
from api.user.actions import _create_new_user
from db.session import get_db

user_router = APIRouter()

@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    try:
        return await _create_new_user(body, db)
    except IntegrityError as err:
        await db.rollback()
        err_detail = str(err.orig)
        if "users_username_key" in err_detail:
            detail = "A user with this username already exists."
            raise HTTPException(status_code=400, detail=detail)
        else:
            detail = "An internal server error occurred."
            raise HTTPException(
                status_code=400 if "already exists" in detail else 500, detail=detail
            )
