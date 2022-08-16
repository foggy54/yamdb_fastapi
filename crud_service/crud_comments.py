from typing import Any, List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import models
from models.database import get_session
from fastapi.encoders import jsonable_encoder

from schemas.schemas import CommentIn, CommentOut
from services.utils import (
    create_access_token,
    create_refresh_token,
    get_hashed_password,
    verify_password,
)
from .crud_base import CRUDBase


class CommentService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
        self.model = models.Comment

    def create(
        self, *, obj_in: CommentIn, user: models.User, review_id: int
    ) -> models.Comment:
        review = (
            self.session.query(self.model)
            .filter(self.model.id == review_id)
            .first()
        )
        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review is not found",
            )
        db_obj = self.model(
            text=obj_in.text,
            author_id=user.id,
            review_id=review_id,
        )
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        response = jsonable_encoder(db_obj)
        comment = CommentOut(author=user.username, **response)
        return comment

    def get_multi(self, review_id: int, skip: int = 0, limit: int = 100):
        query = (
            self.session.query(self.model)
            .filter(self.model.review_id == review_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        response = []
        for comment in query:
            comment_dic = jsonable_encoder(comment)
            comment_dic = CommentOut(author=comment.author.username, **comment_dic)
            response.append(comment_dic)
        return response
