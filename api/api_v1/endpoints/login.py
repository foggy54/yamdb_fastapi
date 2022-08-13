from typing import List, Optional, Union

from crud_service.crud_categories import CategoryService
from crud_service.crud_users import TokenService, UserService
from crud_service.crud_titles import TitleService

# from services.crud_service import CategoryService, UserService, TitleService
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from models.models import User
from schemas.schemas import Category, TitleBase
from schemas.user import (
    Roles,
    TokenRequest,
    TokenSchema,
    UserPatchInput,
    UserSerializer,
    UserSerializerInput,
)
from services.utils import get_current_user


router = APIRouter()


@router.post(
    '/signup', summary="Create new user", response_model=UserSerializerInput
)
def create_user(
    user_data: UserSerializerInput, service: UserService = Depends()
):
    return service.create_user(user_data)


@router.post(
    '/login',
    summary='Create access and refresh tokens for user',
    response_model=TokenSchema,
)
def create_token(
    form_data: TokenRequest,
    service: TokenService = Depends(),
):
    return service.login_access_token(form_data)