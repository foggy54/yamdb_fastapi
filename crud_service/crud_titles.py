from typing import List, Optional, Union, Any
from datetime import datetime
from unicodedata import category
from sqlalchemy.sql import func

from fastapi import Depends, FastAPI, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session
from sqlalchemy import update
from models import models

from models.database import get_session
from pydantic import ValidationError
from schemas.user import (
    Roles,
    TokenRequest,
    TokenSchema,
    UserPatchInput,
    UserSerializer,
    UserSerializerInput,
    TokenPayload,
)
from schemas.schemas import Category, TitleBase
from services.permissions import UserPermissions
from fastapi.encoders import jsonable_encoder


from services.utils import (
    create_access_token,
    create_refresh_token,
    get_hashed_password,
    verify_password,
)


class TitleService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_titles(self, user: models.User):
        if UserPermissions.admin_or_moderator_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access is forbidden",
            )
        query = self.session.query(models.Title).all()
        response = []
        for title in query:
            dic = jsonable_encoder(title)
            rating = (
                self.session.query(
                    func.avg(models.Review.score).label('rating')
                )
                .filter(models.Review.title_id == title.id)
                .scalar()
            )
            if rating is not None:
                dic.update({'rating': round(rating, 2)})
            else:
                dic.update({'rating': None})
            response.append(dic)
        return response

    def get_title_by_id(self, user: models.User, title_id: int):
        if UserPermissions.admin_or_moderator_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access is forbidden",
            )
        query = (
            self.session.query(models.Title)
            .where(models.Title.id == title_id)
            .first()
        )
        rating = (
            self.session.query(func.avg(models.Review.score).label('rating'))
            .filter(models.Review.title_id == title_id)
            .scalar()
        )

        response = jsonable_encoder(query)
        response.update({'rating': round(rating, 2)})
        return response

    def create_title(self, data: TitleBase, user: models.User) -> models.Title:
        if UserPermissions.admin_or_moderator_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access is forbidden",
            )
        data = data.dict()
        name = data.get('name')
        title = (
            self.session.query(models.Title)
            .filter(models.Title.name == name)
            .first()
        )
        if title is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title already exist",
            )
        category = data.pop('category')
        category = (
            self.session.query(models.Category)
            .where(models.Category.name == category.get('name'))
            .first()
        )
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No such Category",
            )
        data['category'] = category
        print(data)
        title = models.Title(**data)
        self.session.add(title)
        self.session.commit()
        self.session.refresh(title)
        return title

    def edit_title(
        self, data: TitleBase, user: models.User, title_id: int
    ) -> models.Title:
        if UserPermissions.admin_or_moderator_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access is forbidden",
            )
        title = self.session.get(models.Title, title_id)
        if not title:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No such title."
            )
        data = data.dict(exclude_unset=True)
        if data.get('category'):
            category = data.pop('category')
            category = (
                self.session.query(models.Category)
                .where(models.Category.name == category.get('name'))
                .first()
            )            
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No such Category",
                )
            data['category_id'] = category.id
        for key, value in data.items():
            setattr(title, key, value)
        self.session.add(title)
        self.session.commit()
        self.session.refresh(title)
        return title

    def delete_title_by_id(self, user: models.User, title_id: int):
        if UserPermissions.admin_or_moderator_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access is forbidden",
            )
        query = (
            self.session.query(models.Title)
            .where(models.Title.id == title_id)
            .first()
        )
        if query is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Title not found.",
            )
        self.session.delete(query)
        self.session.commit()
        return None
