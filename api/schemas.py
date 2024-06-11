from pydantic import BaseModel
from pydantic import constr

class TuneModel(BaseModel):
    class config:
        from_attributes = True

class ShowUser(TuneModel):
    username: str

class UserCreate(BaseModel):
    username: constr(min_length=1, max_length=50) # type: ignore
    password: constr(min_length=1, max_length=100) # type: ignore
