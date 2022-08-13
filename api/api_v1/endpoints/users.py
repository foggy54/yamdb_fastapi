from typing import List, Optional, Union

from crud_service.crud_categories import CategoryService
from crud_service.crud_users import UserService
from crud_service.crud_titles import TitleService

# from services.crud_service import CategoryService, UserService, TitleService
from fastapi import APIRouter, Depends, Response, status, Security
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
from services.utils import get_current_user, get_allowed_user
from services.roles import Role

router = APIRouter()


@router.get("/", summary='Get all users', response_model=List[UserSerializer])
def get_users(
    roles: Roles or None = None,
    user: User = Security(
        get_allowed_user,
        scopes=[Role.ADMIN['name'], Role.MODERATOR['name']],
    ),
    service: UserService = Depends(),
):
    
    return service.get_list_users(roles=roles, user=user)


@router.get(
    '/me',
    summary='Get information about logged user.',
    response_model=UserSerializer,
)
def get_me(user: UserSerializer = Depends(get_current_user)):
    return user


@router.put(
    '/me',
    summary='Patch information about logged user.',
    response_model=UserSerializer,
)
def edit_self(
    user_data: UserPatchInput,
    user: User = Depends(get_current_user),
    service: UserService = Depends(),
):
    return service.patch_user(logged_user=user, user_data=user_data)


@router.get(
    '/{username}',
    summary='Get user by username',
    response_model=UserSerializer,
)
def get_user_by_username(
    username: str,
    user: User = Security(
        get_allowed_user,
        scopes=[Role.ADMIN['name'], Role.MODERATOR['name']],
    ),
    service: UserService = Depends(),
):
    return service.get_user(user, username)
