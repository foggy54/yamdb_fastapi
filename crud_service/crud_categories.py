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


class CategoryService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def create_category(
        self, data: Category, user: models.User
    ) -> models.Category:
        if UserPermissions.admin_or_moderator_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access is forbidden",
            )
        data = data.dict()
        name = data.get('name')
        slug = data.get('slug')
        category = (
            self.session.query(models.Category)
            .filter(models.Category.name == name, models.Category.slug == slug)
            .first()
        )
        if category is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category already exist",
            )
        category = models.Category(**data)
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category
