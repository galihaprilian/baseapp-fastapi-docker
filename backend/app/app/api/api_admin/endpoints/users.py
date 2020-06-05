from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.db import database
from app.utils import send_new_account_email

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
async def read_users(
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = await crud.user.get_all(skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
@database.transaction()
async def create_user(
    *,
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_email_or_username(username=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = await crud.user.create(obj_in=user_in)
    if settings.EMAILS_ENABLED and user_in.email:
        await send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
    return user

@router.get("/{user_id}", response_model=schemas.User)
async def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get a specific user by id.
    """
    user = await crud.user.get(id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    return user


@router.put("/{user_id}", response_model=schemas.User)
@database.transaction()
async def update_user(
    *,
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get(id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    return await crud.user.update(db_obj=user, obj_in=user_in)

@router.delete("/{user_id}", response_model=schemas.User)
@database.transaction()
async def delete_user(
    *,
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get(id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    await crud.user.delete(id=user_id)
    return user
