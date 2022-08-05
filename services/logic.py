from typing import List, Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from models import models
from models.database import get_session
from serializers.user import Roles, UserSerializerInput
from services.utils import get_hashed_password


class UserService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_list(self, roles: Optional[Roles] = None) -> List[models.User]:
        query = self.session.query(models.User)
        if roles:
            query = query.filter_by(role=roles)
        users = query.all()
        return users

    def create(self, user_data: UserSerializerInput) -> models.User:

        user_data = user_data.dict()
        password = user_data.pop('password')
        user_data['hashed_password'] = get_hashed_password(password)
        user = models.User(**user_data)        
        self.session.add(user)
        self.session.commit()
        print(user.__dict__)
        #user.__dict__.pop('hashed_password')
        user.__dict__['password'] = 'hided'
        return user
