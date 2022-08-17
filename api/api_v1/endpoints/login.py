from crud_service.crud_users import TokenService, UserService


from schemas.user import (
    TokenRequest,
    TokenSchema,
    UserSerializerInput,
)
from fastapi import APIRouter, Depends

router = APIRouter()


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
    service: TokenService = Depends(),
):
    return service.login_access_token(form_data)