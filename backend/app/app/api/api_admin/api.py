from fastapi import APIRouter

from app.api.api_admin.endpoints import (
    users,
    utils,
)

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
