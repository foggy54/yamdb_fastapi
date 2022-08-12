from fastapi import APIRouter
from .urls import api_router as operations_router


router = APIRouter()
router.include_router(operations_router)