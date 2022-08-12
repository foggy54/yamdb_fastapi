from typing import List, Optional, Union

from crud_service.crud_categories import CategoryService
from crud_service.crud_users import UserService
from crud_service.crud_titles import TitleService
# from services.crud_service import CategoryService, UserService, TitleService
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from models.models import User
from schemas.schemas import Category, TitleBase
from schemas.user import (Roles, TokenRequest, TokenSchema, UserPatchInput,
                          UserSerializer, UserSerializerInput)
from services.utils import get_current_user





from api.api_v1.endpoints import categories_genres, login, titles, users

api_router = APIRouter(prefix='/api/v1')
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(titles.router, prefix="/titles", tags=["titles"])
api_router.include_router(categories_genres.router, prefix="/categories", tags=["categories"])











