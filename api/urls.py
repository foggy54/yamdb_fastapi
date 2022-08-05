from typing import List, Optional

from fastapi import APIRouter, Depends
from serializers.user import UserSerializer, UserSerializerInput, Roles
from services.logic import UserService

router = APIRouter(prefix='/api')


@router.get("/", response_model=List[UserSerializer])
def get_users(roles: Optional[Roles] = None, service: UserService = Depends()):
    return service.get_list(roles=roles)


@router.post('/', response_model=UserSerializerInput)
def create_user(
    user_data: UserSerializerInput, service: UserService = Depends()
):
    return service.create(user_data)
