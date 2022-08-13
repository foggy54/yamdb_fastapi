from typing import Any, List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import models
from models.database import get_session
from schemas.user import (
    Roles,
    TokenRequest,
    UserPatchInput,
    UserSerializerInput,
)
from services.permissions import UserPermissions
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


class TokenService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def login_access_token(self, form_data: TokenRequest) -> Any:
        """
        OAuth2 compatible token login, get an access token for future requests
        """
        user: models.User = (
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
        if not user.role:
            role = "GUEST"
        else:
            role = user.role

        token_payload = {
            "id": str(user.id),
            "role": role,
        }
        return {
            "access_token": create_access_token(token_payload),
            "token_type": "bearer",
        }
