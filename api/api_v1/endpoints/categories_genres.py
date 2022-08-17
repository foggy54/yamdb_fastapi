from typing import List

# from services.crud_service import CategoryService, UserService, TitleService
from fastapi import APIRouter, Depends, Response, status, Security

from crud_service.crud_categories import CategoryService
from models.models import User
from schemas.schemas import Category
from services.roles import Role
from services.utils import get_allowed_user

router = APIRouter()


@router.post("/", summary="Create the category.", response_model=Category)
def create(
    data_in: Category,
    user: User = Security(
        get_allowed_user,
        scopes=[Role.ADMIN['name'], Role.MODERATOR['name']],
    ),
    service: CategoryService = Depends(),
):
    return service.create(data_in, user)


@router.get(
    "/", summary="Get list of all categories", response_model=List[Category]
)
def get_multi(
    skip: int = 0, limit: int = 100, service: CategoryService = Depends()
):
    return service.get_multi(skip=skip, limit=limit)


@router.delete(
    '/{slug}', summary="Delete selected category.", response_class=Response
)
def remove(
    slug: str,
    response: Response,
    user: User = Security(
        get_allowed_user,
        scopes=[
            Role.ADMIN['name'],
            Role.MODERATOR['name'],
        ],
    ),
    service: CategoryService = Depends(),
):
    response.status_code = status.HTTP_204_NO_CONTENT
    return service.remove(slug)
