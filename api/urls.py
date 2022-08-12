from fastapi import APIRouter

from api.api_v1.endpoints import categories_genres, login, titles, users

api_router = APIRouter(prefix='/api/v1')
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(titles.router, prefix="/titles", tags=["titles"])
api_router.include_router(
    categories_genres.router, prefix="/categories", tags=["categories"]
)
