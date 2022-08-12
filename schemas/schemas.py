from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from typing import Any, Optional, Union


class Category(BaseModel):

    name: str
    slug: str

    class Config:
        orm_mode = True


class TitleBase(BaseModel):

    name: str
    year: int
    description: Optional[str] = None
    category: Union[Category, None] = None
    
    class Config:
        orm_mode = True
        
class Title(TitleBase):
    rating: Union[float, None]


class ReviewBase(BaseModel):
    text: str
    score: int

    class Config:
        orm_mode = True


class Review(ReviewBase):
    id: int
    author: str
    pub_date: datetime

    class Config:
        orm_mode = True
