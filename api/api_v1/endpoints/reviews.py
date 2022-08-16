from typing import List, Optional, Union


from crud_service.crud_titles import TitleService
from crud_service.crud_reviews import ReviewService

# from services.crud_service import CategoryService, UserService, TitleService
from fastapi import APIRouter, Depends, Response, status, Security
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from models.models import User
from schemas.schemas import Category, CommentOut, Review, ReviewBase, TitleBase, Title
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

from .comments import comments_router

reviews_router = APIRouter()
reviews_router.include_router(comments_router, prefix="/{title_id}/reviews/{review_id}", tags=["comments"])


@reviews_router.get(
    "/{title_id}/reviews/{review_id}",
    summary="Get review by id.",
    response_model=Review,
)
def get_review(
    title_id: int,
    review_id: int,
    user: UserSerializer = Depends(get_current_user),
    service: ReviewService = Depends(),
):
    return service.get_review(title_id, review_id, user)


@reviews_router.get(
    "/{title_id}/reviews",
    summary="Get all reviews for selected title.",
    response_model=List[Review],
)
def get_multi(
    title_id: int,
    user: UserSerializer = Depends(get_current_user),
    service: ReviewService = Depends(),
):
    return service.get_multi(title_id, user)


@reviews_router.post(
    '/{title_id}/reviews',
    summary="Post review.",
    response_model=Review,
    tags=["reviews"],
)
def create_review(
    title_id: int,
    data: ReviewBase,
    user: User = Security(
        get_allowed_user,
        scopes=[Role.ADMIN['name'], Role.MODERATOR['name'], Role.USER["name"]],
    ),
    service: ReviewService = Depends(),
):
    return service.create_review(title_id, data, user)