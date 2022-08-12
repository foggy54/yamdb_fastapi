from typing import List, Optional, Union


from crud_service.crud_titles import TitleService
from crud_service.crud_reviews import ReviewService

# from services.crud_service import CategoryService, UserService, TitleService
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from models.models import User
from schemas.schemas import Category, Review, ReviewBase, TitleBase, Title
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


@router.get(
    '/',
    summary="Get information about titles.",
    response_model=List[Title],
)
def get_titles(
    user: UserSerializer = Depends(get_current_user),
    service: TitleService = Depends(),
):
    return service.get_titles(user=user)


@router.get(
    '/{title_id}',
    summary="Get title by id.",
    response_model=Title,
)
def get_title_by_id(
    title_id: int,
    user: UserSerializer = Depends(get_current_user),
    service: TitleService = Depends(),
):
    return service.get_title_by_id(user=user, title_id=title_id)


@router.post('/', summary="Create title.", response_model=TitleBase)
def create_title(
    data: TitleBase,
    user: UserSerializer = Depends(get_current_user),
    service: TitleService = Depends(),
):
    return service.create_title(user=user, data=data)


@router.put(
    '/{title_id}',
    summary="Edit selected title.",
    response_model=TitleBase,
)
def edit_title(
    title_id: int,
    data: TitleBase,
    user: UserSerializer = Depends(get_current_user),
    service: TitleService = Depends(),
):
    return service.edit_title(user=user, title_id=title_id, data=data)


@router.delete(
    '/{title_id}',
    summary='Delete selected title.',
    response_class=Response,
)
def delete_title(
    title_id: int,
    response: Response,
    user: UserSerializer = Depends(get_current_user),
    service: TitleService = Depends(),
):
    response.status_code = status.HTTP_204_NO_CONTENT
    return service.delete_title_by_id(user, title_id)


@router.get(
    "/{title_id}/reviews/{review_id}/",
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


@router.get(
    "/{title_id}/reviews/",
    summary="Get all reviews for selected title.",
    response_model=List[Review],
)
def get_multi(
    title_id: int,
    user: UserSerializer = Depends(get_current_user),
    service: ReviewService = Depends(),
):
    return service.get_multi(title_id, user)


@router.post(
    '/{title_id}/reviews',
    summary="Post review.",
    response_model=Review,
    tags=["reviews"],
)
def create_review(
    title_id: int,
    data: ReviewBase,
    user: UserSerializer = Depends(get_current_user),
    service: ReviewService = Depends(),
):
    return service.create_review(title_id, data, user)
