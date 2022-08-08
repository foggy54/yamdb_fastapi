from typing import List, Optional, Union

from fastapi import APIRouter, Depends
from schemas.user import (
    UserSerializer,
    UserSerializerInput,
    TokenSchema,
    Roles,
    TokenRequest,
)
from services.crud import UserService
from services.utils import get_current_user
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix='/api')


@router.get(
    "/users", summary='Get all users', response_model=List[UserSerializer]
)
def get_users(roles: Roles or None = None, service: UserService = Depends()):
    return service.get_list_users(roles=roles)


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
    service: UserService = Depends(),
):
    return service.issue_token(form_data)


@router.get(
    '/users/me',
    summary='Get information about logged user.',
    response_model=UserSerializer,
)
def get_me(user: UserSerializer = Depends(get_current_user)):
    return user
