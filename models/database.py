from sqlalchemy import (
    create_engine,
)
from services.config import settings
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

Session = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
)


def get_session() -> Session:
    session = Session()
    try:
        yield session
    finally:
        session.close()


