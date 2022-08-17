import os

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']  # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ[
    'JWT_REFRESH_SECRET_KEY'
]  # should be kept secret


class Settings(BaseSettings):
    server_host: str = "127.0.0.1"
    server_port: int = 8000
    database_url: str = 'sqlite:///db.sqlite3'


settings = Settings()
