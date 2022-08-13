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
from services.utils import get_allowed_user
from services.roles import Role

router = APIRouter()

@router.post(
    "/", summary="Create the category.", response_model=Category
)
def create_category(
        category_data: Category,
        user: User = Security(
        get_allowed_user,
        scopes=[Role.ADMIN['name'], Role.MODERATOR['name']],
    ),
        service: CategoryService = Depends(),
):
    return service.create_category(category_data, user)