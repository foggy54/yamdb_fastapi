
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
from permissions import UserPermissions
from fastapi.encoders import jsonable_encoder


from services.utils import (
    create_access_token,
    create_refresh_token,
    get_hashed_password,
    verify_password,
)


class UserService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_list_users(
        self,
        user: models.User,
        roles: Optional[Roles] = None,
    ) -> List[models.User]:
        if UserPermissions.admin_or_moderator_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access is forbidden",
            )
        query = self.session.query(models.User)
        if roles:
            query = query.filter_by(role=roles)
        users = query.all()
        return users

    def get_user(self, user: models.User, username: str):
        if not UserPermissions.admin_or_moderator_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access is forbidden",
            )
        query = (
            self.session.query(models.User)
            .filter(models.User.username == username)
            .first()
        )
        return query

    def create_user(self, user_data: UserSerializerInput) -> models.User:
        if self.validate_user_fields(user_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some required fields not filled.",
            )
        if self.validate_forbidden_username(user_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="It is forbidden to use Me as username.",
            )
        user_data = user_data.dict()
        username = user_data.get('username')
        email = user_data.get('email')
        user = (
            self.session.query(models.User)
            .filter(
                models.User.email == email, models.User.username == username
            )
            .first()
        )
        if user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exist",
            )

        password = user_data.pop('password')
        user_data['hashed_password'] = get_hashed_password(password)
        user = models.User(**user_data)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        user.__dict__['password'] = 'hided'
        return user

    def patch_user(
        self, user_data: UserPatchInput, logged_user: models.User
    ) -> models.User:
        update_user_data = user_data.dict(exclude_unset=True)
        if 'password' in update_user_data:
            password = update_user_data.pop('password')
            update_user_data['hashed_password'] = get_hashed_password(password)

        user = (
            self.session.query(models.User)
            .filter(models.User.id == logged_user.id)
            .update(update_user_data, synchronize_session=False)
        )
        user = (
            self.session.query(models.User)
            .filter(models.User.id == logged_user.id)
            .first()
        )
        self.session.commit()
        return user

    def issue_token(self, form_data: TokenRequest):
        user = (
            self.session.query(models.User)
            .filter(
                models.User.username == form_data.username,
            )
            .first()
        )
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password",
            )
        hashed_pass = user.hashed_password
        if not verify_password(form_data.password, hashed_pass):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password",
            )
        return {
            "access_token": create_access_token(
                subject=user.id, role=user.role
            ),
            "refresh_token": create_refresh_token(user.username),
        }

    def validate_user_fields(self, user_data: UserSerializerInput) -> bool:
        return not (
            user_data.username and user_data.email and user_data.password
        )

    def validate_forbidden_username(
        self, user_data: UserSerializerInput
    ) -> bool:
        return str(user_data.username).lower() == 'me'


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
        return query

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
        return query

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
        data = data.dict()
        data = {key: value for key, value in data.items() if value is not None}
        title = self.session.query(models.Title).filter(
            models.Title.id == title_id
        )
        if data.get('category') is not None:
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
            data['category_id'] = category.id
        title = (
            update(models.Title)
            .where(models.Title.id == title_id)
            .values(**data)
            .execution_options(synchronize_session=False)
        )
        self.session.execute(title)
        title = (
            self.session.query(models.Title)
            .filter(models.Title.id == title_id)
            .first()
        )
        self.session.commit()
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
