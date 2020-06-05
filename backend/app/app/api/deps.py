from typing import Generator

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    SecurityScopes,
)
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db import database

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/access-token",
    scopes={
        "me": "All information about me",
        "super": "Superuser"
    }
)

async def get_current_user(
    security_scopes: SecurityScopes, 
    token: str = Depends(oauth2_scheme)
) -> models.User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
        if token_data.sub is None:
            raise credentials_exception
    except (jwt.JWTError, ValidationError):
        raise credentials_exception
    user = await crud.user.get_by_email_or_username(username=token_data.sub)
    if not user:
        raise credentials_exception
    token_scopes = token_data.scopes.split(" ")
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: models.User = Security(get_current_user, scopes=["me"]),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
    current_user: models.User = Security(get_current_user, scopes=["super"]),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
