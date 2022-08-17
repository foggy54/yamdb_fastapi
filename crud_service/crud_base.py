from typing import Any, Generic, List, Optional, Type, TypeVar

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.database import get_session
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

    def remove(self, *, id: int) -> None:
        obj = self.session.query(self.model).get(id)
        if obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found.",
            )
        self.session.delete(obj)
        self.session.commit()
        return None
