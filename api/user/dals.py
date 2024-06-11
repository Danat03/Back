from typing import Union
from typing import cast
from uuid import UUID
from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User

class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self, username: str, hashed_password: str
    ) -> User:
        new_user = User(username=username, hashed_password=hashed_password)
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user
    
    async def get_user_by_username(self, username: str) -> Union[User, None]:
        query = select(User).filter(cast("ColumnElement[bool]", User.username == username))
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]
        
    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        query = select(User).filter(cast("ColumnElement[bool]", User.user_id == user_id))
        res = await self.db_session.execute(query)
        user_row = res.scalars().first()
        if user_row is not None:
            return user_row
