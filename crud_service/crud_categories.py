from fastapi import Depends, HTTPException, status
from sqlalchemy import delete
from sqlalchemy.orm import Session

from models import models
from models.database import get_session
from schemas.schemas import Category
from .crud_base import CRUDBase


class CategoryService(CRUDBase[models.Category]):
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
        self.model = models.Category

    def create(self, data: Category, user: models.User) -> models.Category:
        data = data.dict()
        name = data.get('name')
        slug = data.get('slug')
        category = (
            self.session.query(self.model)
            .filter(self.model.name == name, self.model.slug == slug)
            .first()
        )
        if category is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category already exist",
            )
        category = self.model(**data)
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def remove(self, slug: str):
        query = delete(self.model).where(self.model.slug == slug)
        self.session.execute(query)
        self.session.commit()
        return None
