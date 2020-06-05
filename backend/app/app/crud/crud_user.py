from typing import Any, Dict, Optional, Union

from app.db import database

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, *, email: str) -> Optional[User]:
        query = self.table.select().where(self.table.c.email == email)
        user = await database.fetch_one(query=query)
        if not user:
            return None
        return User(**user)

    async def get_by_email_or_username(self, *, username: str) -> Optional[User]:
        query = (
            self.table
            .select()
            .where((self.table.c.username == username) | \
                (self.table.c.email == username))
        )
        user = await database.fetch_one(query=query)
        if not user:
            return None
        return User(**user)

    async def create(self, *, obj_in: [UserCreate, Dict[str, Any]]) -> User:
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = obj_in.dict()
        obj_in_data["hashed_password"] = get_password_hash(obj_in.password)
        del obj_in_data["password"]
        return await super().create(obj_in=obj_in_data)

    async def update(self, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> Any:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password", None):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await super().update(db_obj=db_obj, obj_in=update_data)

    async def authenticate(self, *, username: str, password: str) -> Optional[User]:
        user = await self.get_by_email_or_username(username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def get_scopes(self, user: User) -> str:
        return "me super" if user.is_superuser else "me"

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user = CRUDUser(User)
