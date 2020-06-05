from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.db import database
from app.core.config import settings
from app.utils import send_new_account_email

router = APIRouter()


@router.put("/", response_model=schemas.User)
@database.transaction()
async def update_user_me(
    *,
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    user_in = {}
    if password is not None:
        user_in["password"] = password
    if full_name is not None:
        user_in["full_name"] = full_name
    if email is not None:
        user_in["email"] = email
    return await crud.user.update(db_obj=current_user, obj_in=user_in)


@router.get("/", response_model=schemas.User)
async def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=schemas.User)
@database.transaction()
async def create_user_open(
    *,
    password: str = Body(...),
    email: EmailStr = Body(...),
    full_name: str = Body(None),
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = await crud.user.get_by_email_or_username(username=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user_in = schemas.UserCreate(password=password, email=email, username=email, full_name=full_name)
    return await crud.user.create(obj_in=user_in)
