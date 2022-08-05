from pydantic import BaseModel
from enum import Enum
from typing import Optional


class Roles(str, Enum):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class UserSerializerInput(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    password: str
    role: Roles

    class Config:
        orm_mode = True


class UserSerializer(UserSerializerInput):
    id: int
    hashed_password: Optional[str]

    class Config:
        orm_mode = True
