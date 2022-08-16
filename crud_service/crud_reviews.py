from datetime import datetime
from typing import Any, List, Optional, Union
from unicodedata import category

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from models import models
from models.database import get_session
from pydantic import ValidationError
from schemas.schemas import Category, Review, ReviewBase, TitleBase
from schemas.user import (
    Roles,
    TokenPayload,
    TokenRequest,
    TokenSchema,
    UserPatchInput,
    UserSerializer,
    UserSerializerInput,
)
from services.permissions import UserPermissions
from services.utils import (
    create_access_token,
    create_refresh_token,
    get_hashed_password,
    verify_password,
)
from sqlalchemy import update
from sqlalchemy.orm import Session


class ReviewService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_review(self, title_id: int, review_id: int, user: models.User):
        query = (
            self.session.query(models.Review)
            .filter(
                models.Review.title_id == title_id,
                models.Review.id == review_id,
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
        query = self.session.query(models.Review).filter(
            models.Review.title_id == title_id
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
        review = models.Review(**data)
        self.session.add(review)
        self.session.commit()
        self.session.refresh(review)
        response = jsonable_encoder(review)
        review = Review(author=user.username, **response)

        return review
