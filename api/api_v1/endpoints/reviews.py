from typing import List

from fastapi import APIRouter, Depends, Response, status, Security

from crud_service.crud_reviews import ReviewService
from models.models import User
from schemas.schemas import (
    Review,
    ReviewBase,
)
from schemas.user import (
    UserSerializer,
)
from services.roles import Role
from services.utils import get_current_user, get_allowed_user
from .comments import comments_router

reviews_router = APIRouter()
reviews_router.include_router(
    comments_router,
    prefix="/{title_id}/reviews/{review_id}/comments",
    tags=["comments"],
)


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


@reviews_router.delete(
    "/{title_id}/reviews/{review_id}",
    summary="Delete selected review",
    response_class=Response,
)
def remove(
    review_id: int,
    response: Response,
    user: User = Security(
        get_allowed_user,
        scopes=[
            Role.ADMIN['name'],
            Role.MODERATOR['name'],
        ],
    ),
    service: ReviewService = Depends(),
):
    response.status_code = status.HTTP_204_NO_CONTENT
    return service.remove(review_id)
