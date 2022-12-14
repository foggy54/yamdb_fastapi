from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel


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


class CommentIn(BaseModel):
    text: str

    class Config:
        orm_mode = True


class CommentOut(BaseModel):
    id: int
    text: str
    author: str
    pub_date: datetime

    class Config:
        orm_mode = True
