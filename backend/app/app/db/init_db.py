from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.db import database, base  # noqa: F401

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


async def init_db() -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    user = await crud.user.get_by_email_or_username(username=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            username=settings.FIRST_SUPERUSER,
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            is_active=True
        )
        user = await crud.user.create(obj_in=user_in)  # noqa: F841
