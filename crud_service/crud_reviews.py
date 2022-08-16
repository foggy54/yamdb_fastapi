from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from models import models
from models.database import get_session
from schemas.schemas import Review, ReviewBase
from .crud_base import CRUDBase


class ReviewService(CRUDBase[models.Review]):
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
        self.model = models.Review

    def get_review(self, title_id: int, review_id: int, user: models.User):
        query = (
            self.session.query(self.model)
            .filter(
                self.model.title_id == title_id,
                self.model.id == review_id,
            )
            .first()
        )
        if query is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No reviews found",
            )
        response = jsonable_encoder(query)
        response = Review(author=query.author.username, **response)
        return response

    def get_multi(self, title_id: int, user: models.User):
        title = (
            self.session.query(models.Title)
            .filter(models.Title.id == title_id)
            .first()
        )
        if title is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Title not found",
            )
        query = self.session.query(self.model).filter(
            self.model.title_id == title_id
        )
        if query is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review is not found",
            )
        response = []
        for review in query:
            review_dic = jsonable_encoder(review)
            review_dic = Review(author=review.author.username, **review_dic)
            response.append(review_dic)
        return response

    def create_review(
        self, title_id: int, data: ReviewBase, user: models.User
    ):
        title = (
            self.session.query(models.Title)
            .filter(models.Title.id == title_id)
            .first()
        )
        if title is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Title not found",
            )
        data = jsonable_encoder(data)
        data['author_id'] = user.id
        data['title_id'] = title_id
        review = self.model(**data)
        self.session.add(review)
        self.session.commit()
        self.session.refresh(review)
        response = jsonable_encoder(review)
        review = Review(author=user.username, **response)
        return review
