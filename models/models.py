import asyncio
from datetime import datetime

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, MetaData,
                        Numeric, SmallInteger, String, Table, Text,
                        create_engine)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import (backref, relation, relationship, scoped_session,
                            sessionmaker, validates)

from .database import engine, Session


# db_session = scoped_session(
#     sessionmaker(autocommit=False, autoflush=False, bind=engine)
# )

Base = declarative_base()
#Base.query = Session.query_property()


def init_db():
    Base.metadata.create_all(engine)


MAX_LENGTH_SHORT = 50
MAX_LENGTH_MED = 150
MAX_LENGTH_LONG = 254
MAX_LEN_TEXT = 3


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(MAX_LENGTH_SHORT), nullable=False)
    first_name = Column(String(MAX_LENGTH_SHORT), nullable=True)
    last_name = Column(String(MAX_LENGTH_SHORT), nullable=True)
    hashed_password = Column(String(MAX_LENGTH_LONG), nullable=True)
    email = Column(String(MAX_LENGTH_LONG), nullable=True)
    role = Column(String(MAX_LENGTH_SHORT), nullable=False)


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_LENGTH_SHORT), nullable=False)
    slug = Column(String(MAX_LENGTH_SHORT), nullable=False)

    def __str__(self):
        return self.name


class Genre(Base):
    __tablename__ = 'genre'
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_LENGTH_SHORT), nullable=False)
    slug = Column(String(MAX_LENGTH_SHORT), nullable=False)

    def __str__(self):
        return self.name


class Title(Base):
    __tablename__ = 'title'
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_LENGTH_SHORT), nullable=False)
    year = Column(SmallInteger, nullable=False)
    description = Column(String(500), nullable=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", backref="titles")


class Review(Base):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    title_id = Column(
        Integer,
        ForeignKey('title.id', ondelete="CASCADE"),
        nullable=True,
    )
    title = relationship('Title', backref='reviews')
    text = Column(Text, nullable=True)
    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship('User', backref='reviews')
    score = Column(SmallInteger)
    pub_date = Column(DateTime, default=datetime.now)

    @validates('score')
    def validate_score(self, value):
        if value < 1 or value > 10:
            raise ValueError("score must be in interval from 1 to 10")
        return value


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True)
    review_id = Column(
        Integer,
        ForeignKey('review.id', ondelete="CASCADE"),
        nullable=False,
    )
    review = relationship('Review', backref='comments')
    text = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship('User', backref='comments')
    pub_date = Column(DateTime, default=datetime.now)


if __name__ == "__main__":
    init_db()
