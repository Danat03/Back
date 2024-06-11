from typing import Union

from api.schemas import ShowUser, UserCreate
from api.user.dals import UserDAL
from db.models import User
from hashing import Hasher


async def _create_new_user(body: UserCreate, session) -> ShowUser:
    try:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(
                username=body.username,
                hashed_password=Hasher.get_password_hash(body.password),
            )
            await session.commit()
            return ShowUser(
                username=user.username,
            )
    except Exception:
        await session.rollback()
        raise

async def _get_user_by_id(user_id, session) -> Union[User, None]:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_id(
            user_id=user_id
        )
        if user is not None:
            return user
        