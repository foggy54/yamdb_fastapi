from typing import List, Optional, Union, Any
from datetime import datetime
from unicodedata import category

from fastapi import Depends, FastAPI, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session
from sqlalchemy import update
from models import models

from models.database import get_session

from schemas.schemas import Category, TitleBase
from services.permissions import UserPermissions
from fastapi.encoders import jsonable_encoder
from .crud_base import CRUDBase
from sqlalchemy import delete


class CategoryService(CRUDBase[models.Category]):
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
        self.model = models.Category

    def create(self, data: Category, user: models.User) -> models.Category:
        data = data.dict()
        name = data.get('name')
        slug = data.get('slug')
        category = (
            self.session.query(self.model)
            .filter(self.model.name == name, self.model.slug == slug)
            .first()
        )
        if category is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category already exist",
            )
        category = self.model(**data)
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def remove(self, slug: str):
        query = delete(self.model).where(self.model.slug == slug)
        self.session.execute(query)
        self.session.commit()
        return None
