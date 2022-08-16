from typing import List, Optional, Union


from crud_service.crud_titles import TitleService
from crud_service.crud_reviews import ReviewService

# from services.crud_service import CategoryService, UserService, TitleService
from fastapi import APIRouter, Depends, Response, status, Security
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from models.models import User
from schemas.schemas import Category, Review, ReviewBase, TitleBase, Title, CommentIn, CommentOut
from schemas.user import (
    Roles,
    TokenRequest,
    TokenSchema,
    UserPatchInput,
    UserSerializer,
    UserSerializerInput,
)
from crud_service.crud_comments import CommentService
from services.utils import get_current_user, get_allowed_user
from services.roles import Role

comments_router = APIRouter()

@comments_router.get(
    '/comments',
    summary="Get all comments for the review.",
    response_model=List[CommentOut],
)
def get_comments(
    review_id: int,
    skip: int = 0,
    limit: int = 100,
    user: UserSerializer = Depends(get_current_user),
    service: CommentService = Depends(),
):
    return service.get_multi(skip=skip, limit=limit, review_id=review_id)


@comments_router.post(
    '/comments',
    summary="Create comment to the review.",
    response_model=CommentOut,
)
def create_comment(
    review_id:int,
    data_in: CommentIn,
    user: User = Security(
        get_allowed_user,
        scopes=[Role.ADMIN['name'], Role.MODERATOR['name']],
    ),
    service: CommentService = Depends(),
):
    return service.create(obj_in=data_in, user=user, review_id=review_id)