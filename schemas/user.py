from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union
from pydantic.networks import EmailStr


class Roles(str, Enum):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str


class UserSerializerInput(UserBase):
    password: str

    class Config:
        orm_mode = True


class UserSerializer(UserBase):
    id: int
    role: Roles

    class Config:
        orm_mode = True


class UserPatchInput(BaseModel):
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    password: Union[str, None] = None

    class Config:
        orm_mode = True


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    id: int
    role: str
    exp: int
