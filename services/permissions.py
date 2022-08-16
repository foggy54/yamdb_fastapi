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


class UserPermissions:
    @staticmethod
    def admin_access(user: models.User) -> bool:
        return user.role != 'admin'

    @staticmethod
    def admin_or_moderator_access(user: models.User) -> bool:
        return not user.role in ('admin', 'moderator')

    @staticmethod
    def admin_or_moderator_or_self_access(
        user: models.User, author: models.User
    ):
        if author.username != user.username:
            return True
        return not user.role in ('admin', 'moderator')
