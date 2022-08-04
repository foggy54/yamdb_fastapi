from pydantic import BaseModel
from enum import Enum

class Roles(str, Enum):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

class UserSerializerInput(BaseModel):
    username: str
    first_name: str
    last_name: str
    hashed_password: str
    email: str
    role: Roles
    
    class Config:
        orm_mode = True
    

class UserSerializer(UserSerializerInput):
    id: int
    username: str
    first_name: str
    last_name: str
    hashed_password: str
    email: str
    role: Roles
    
    class Config:
        orm_mode = True