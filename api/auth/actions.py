from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession

from hashing import Hasher
from db.models import User
from api.user.dals import UserDAL

async def authenticate_user(username: str, password: str, session: AsyncSession) -> Union[User, None]:
    user = await _get_user_by_username_for_auth(username=username, session=session)
    if user is None:
        return
    if not Hasher.verify_password(password, user.hashed_password):
        return
    return user

async def _get_user_by_username_for_auth(username: str, session: AsyncSession):
    async with session.begin():
        user_dal = UserDAL(session)
        return await user_dal.get_user_by_username(username=username)
    