from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from models.database import get_session
from fastapi import Depends
from models.models import Base


ModelType = TypeVar("ModelType", bound=Base)



class CRUDBase(Generic[ModelType]):
    def __init__(
        self, model: Type[ModelType], session: Session = Depends(get_session)
    ):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
        self.session = session

    def get(self, id: Any) -> Optional[ModelType]:
        return (
            self.session.query(self.model).filter(self.model.id == id).first()
        )

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def remove(self, *, id: int) -> ModelType:
        obj = self.session.query(self.model).get(id)
        self.session.delete(obj)
        self.session.commit()
        return obj
