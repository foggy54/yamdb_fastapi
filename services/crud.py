from typing import List, Optional, Union, Any
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session
from models import models

from models.database import get_session
from pydantic import ValidationError
from schemas.user import (
    Roles,
    TokenRequest,
    TokenSchema,
    UserSerializer,
    UserSerializerInput,
    TokenPayload,
)


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
        self, roles: Optional[Roles] = None
    ) -> List[models.User]:
        query = self.session.query(models.User)
        if roles:
            query = query.filter_by(role=roles)
        users = query.all()
        return users

    def create_user(self, user_data: UserSerializerInput) -> models.User:
        if not self.validate_user_fields(user_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some required fields not filled.",
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
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.username),
        }

    def validate_user_fields(self, user_data: UserSerializerInput) -> bool:
        return user_data.username and user_data.email and user_data.password
