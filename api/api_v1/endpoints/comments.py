from typing import List

from fastapi import APIRouter, Depends, Security

from crud_service.crud_comments import CommentService
from models.models import User
from schemas.schemas import (
    CommentIn,
    CommentOut,
)
from schemas.user import (
    UserSerializer,
)
from services.roles import Role
from services.utils import get_current_user, get_allowed_user

comments_router = APIRouter()


@comments_router.get(
    '/',
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
    '/',
    summary="Create comment to the review.",
    response_model=CommentOut,
)
def create_comment(
    review_id: int,
    data_in: CommentIn,
    user: User = Security(
        get_allowed_user,
        scopes=[Role.ADMIN['name'], Role.MODERATOR['name'], Role.USER['name']],
    ),
    service: CommentService = Depends(),
):
    return service.create(obj_in=data_in, user=user, review_id=review_id)


@comments_router.put(
    "/{comment_id}",
    summary="Edit selected comment",
)
def update(
    comment_id: int,
    data_in: CommentIn,
    user: User = Security(
        get_allowed_user,
        scopes=[Role.ADMIN['name'], Role.MODERATOR['name'], Role.USER['name']],
    ),
    service: CommentService = Depends(),
):
    return service.update(data_in, user, comment_id)


@comments_router.delete(
    '/{comment_id}',
    summary='Delete selected comment.',
)
def delete_comment(
    comment_id: int,
    user: User = Security(
        get_allowed_user,
        scopes=[Role.ADMIN['name'], Role.MODERATOR['name'], Role.USER['name']],
    ),
    service: CommentService = Depends(),
):
    return service.remove(id=comment_id)
