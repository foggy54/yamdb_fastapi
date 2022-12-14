from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from models import models
from models.database import get_session
from schemas.schemas import TitleBase


class TitleService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_titles(self, user: models.User):
        query = self.session.query(models.Title).all()
        response = []
        for title in query:
            dic = jsonable_encoder(title)
            rating = (
                self.session.query(
                    func.avg(models.Review.score).label('rating')
                )
                .filter(models.Review.title_id == title.id)
                .scalar()
            )
            if rating is not None:
                dic.update({'rating': round(rating, 2)})
            else:
                dic.update({'rating': None})
            response.append(dic)
        return response

    def get_title_by_id(self, user: models.User, title_id: int):
        query = (
            self.session.query(models.Title)
            .where(models.Title.id == title_id)
            .first()
        )
        rating = (
            self.session.query(func.avg(models.Review.score).label('rating'))
            .filter(models.Review.title_id == title_id)
            .scalar()
        )

        response = jsonable_encoder(query)
        if rating:
            response.update({'rating': round(rating, 2)})
        return response

    def create_title(self, data: TitleBase, user: models.User) -> models.Title:
        data = data.dict()
        name = data.get('name')
        title = (
            self.session.query(models.Title)
            .filter(models.Title.name == name)
            .first()
        )
        if title is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title already exist",
            )
        category = data.pop('category')
        category = (
            self.session.query(models.Category)
            .where(models.Category.name == category.get('name'))
            .first()
        )
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No such Category",
            )
        data['category'] = category
        title = models.Title(**data)
        self.session.add(title)
        self.session.commit()
        self.session.refresh(title)
        return title

    def edit_title(
        self, data: TitleBase, user: models.User, title_id: int
    ) -> models.Title:
        title = self.session.get(models.Title, title_id)
        if not title:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No such title."
            )
        data = data.dict(exclude_unset=True)
        if data.get('category'):
            category = data.pop('category')
            category = (
                self.session.query(models.Category)
                .where(models.Category.name == category.get('name'))
                .first()
            )
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No such Category",
                )
            data['category_id'] = category.id
        for key, value in data.items():
            setattr(title, key, value)
        self.session.add(title)
        self.session.commit()
        self.session.refresh(title)
        return title

    def delete_title_by_id(self, user: models.User, title_id: int):
        query = (
            self.session.query(models.Title)
            .where(models.Title.id == title_id)
            .first()
        )
        if query is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Title not found.",
            )
        self.session.delete(query)
        self.session.commit()
        return None
